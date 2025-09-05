import datetime
import logging
import uuid
from collections.abc import Iterable
from itertools import count

import httpx

from lerppu.inference.size import get_mb_size_from_name
from lerppu.inference.type import get_connection_type_from_data
from lerppu.inference.vendor import canonicalize_vendor
from lerppu.models import MediaType, Product

log = logging.getLogger(__name__)

dustin_session_id = uuid.UUID(
    int=int(datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000),
)


def massage_dustinhome(
    prod: dict,
    media_type: MediaType,
) -> Product:
    prod = prod["searchResultProduct"]
    name = f"{prod['manufacturerName']} {prod['displayName']}"
    desc = prod["displaySpecifications"]
    specs = {s["name"]: s["value"] for s in prod["promotedSpecifications"]}
    size = None
    if specs.get("Muistin koko"):
        size = get_mb_size_from_name(specs["Muistin koko"])
    if not size:
        size = get_mb_size_from_name(f"{name} {desc}")
    connection_type = get_connection_type_from_data(
        [
            specs.get("Liitin"),
            name,
            desc,
        ]
    )
    return Product(
        media_type=media_type,
        connection_type=connection_type,
        id=f"dustinhome:{prod['id']}",
        source="dustinhome",
        name=name,
        size_mb=size,
        original_price=prod["price"]["originalPrice"],
        current_price=prod["price"]["price"],
        url=f"https://www.dustinhome.fi/product/{prod['id']}",
        vendor_sku=prod["manufacturerProductIdentifier"],
        manufacturer=canonicalize_vendor(prod["manufacturerName"]),
        _original=prod,
    )


GET_CATEGORY_FOR_FILTER_PAGE_QUERY = """
query GetCategoryForFilterPage($categoryId: String!, $searchPhrase: String, $sortBy: SortBy!, $page: Int!, $pageSize: Int!, $facets: [FacetParameterInput!]) {
  category(categoryId: $categoryId) {
    id
    seoTitle
    seoMetaDescription
    name
    namePath
    pathSlug
    seoText
    seoLongTitleName
    navigation(facets: $facets) {
      id
      path {
        ...NavigationItem
      }
      siblings {
        ...NavigationItem
      }
      childrenSortedByHits {
        ...ChildNavigationItem
      }
    }
    productSearch(
      searchPhrase: $searchPhrase
      sortBy: $sortBy
      page: $page
      pageSize: $pageSize
      facets: $facets
    ) {
      facets {
        name
        type
        displayName
        facetOpened
        nameInUrl
        isTranslated
        unitText
        values {
          displayName
          name
          hits
          min
          max
        }
      }
      filterOnlyFacets {
        name
        type
        displayName
        facetOpened
        nameInUrl
        isTranslated
        unitText
        values {
          displayName
          name
          hits
          min
          max
        }
      }
      productHits
      productReferences {
        ...ProductReference
      }
      ads {
        ...Ads
      }
    }
  }
}

fragment NavigationItem on CategoryNavigationItem {
  categoryId
  hits
  selected
  category {
    name
    pathSlug
    categoryImageFileName
  }
}

fragment ChildNavigationItem on ProductCategoryChildNavigationItem {
  categoryId
  hits
  selected
  category {
    name
    pathSlug
    categoryImageFileName
  }
}

fragment ProductReference on ProductReference {
  id
  ticket
  searchResultProduct {
    ...ProductForList
  }
}

fragment Ads on AdContainer {
  banner {
    imageUrl
    url
    text
    displayMode
    buttonText
  }
  productReferences {
    ...ProductReference
  }
  bannerId
  ticket
}

fragment ProductForList on SearchResultProduct {
  id
  productErpIdentifier
  displayName
  primaryImageId
  manufacturerName
  manufacturerProductIdentifier
  manufacturerErpIdentifier
  displaySpecifications
  oneLiner
  internalProduct
  nameSlug
  energyClass
  energyDocumentId
  energyLabelImageId
  reviewScore
  isNewProduct
  minQuantityPerOrder
  promotedSpecifications(take: 4) {
    name
    value
  }
  price {
    campaignPercentage
    campaignType
    formatted {
      price
      originalPrice
      priceExcludingVat
      priceIncludingVat
    }
    isBestSeller
    isBid
    isCampaign
    isRecommendedProduct
    price
    priceExcludingVat
    priceIncludingVat
    originalPrice
    priceVat
  }
  categoryName
  categoryPathEng
  availability {
    maxAvailableQuantity
    internalEtaStock {
      quantity
      eta
    }
    externalStock {
      leadTime
      quantity
    }
    availabilityDetails {
      formattedDateUtc
      key
    }
    availabilityStatus
    internalStock {
      quantity
      showAlwaysInStock
    }
    isAvailableForSale
    isPreOrder
    productLifeCycleState
    showAvailabilityQuantities
    showEtaDate
  }
}
"""  # noqa: E501


def _get_category_product_page(
    cli: httpx.Client,
    *,
    category_id: str,
    page: int,
):
    query = {
        "query": GET_CATEGORY_FOR_FILTER_PAGE_QUERY,
        "variables": {
            "categoryId": category_id,
            "facets": [],
            "page": page,
            "pageSize": 50,
            "searchPhrase": "",
            "sortBy": "DESC",
        },
        "operationName": "GetCategoryForFilterPage",
    }
    resp = cli.post(
        url="https://www.dustinhome.fi/graphql",
        headers={
            "x-correlation-id": "1",
            "x-dustin-anonymoususeridentifier": str(dustin_session_id),
            "x-dustin-contactid": "0",
            "x-dustin-language": "Finnish",
            "x-dustin-sessionkey": str(dustin_session_id),
            "x-dustin-showpriceincludingvat": "true",
            "x-dustin-site": "DustinHomeFinland",
            "x-dustin-temporary-isadmin": "false",
            "referer": "https://www.dustinhome.fi/",
        },
        json=query,
    )
    resp.raise_for_status()
    return resp.json()["data"]["category"]


def get_category_products(
    cli: httpx.Client,
    *,
    category_id: str,
    media_type: MediaType,
) -> Iterable[Product]:
    for page_no in count(1):
        log.info(f"Fetching page {page_no} of category {category_id}")
        data = _get_category_product_page(cli, category_id=category_id, page=page_no)
        products = data.get("productSearch", {}).get("productReferences", [])
        if not products:
            break
        for prod in products:
            yield massage_dustinhome(
                prod,
                media_type=media_type,
            )
