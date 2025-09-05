import logging
from collections.abc import Iterable
from itertools import count

import httpx

from lerppu.inference.size import get_mb_size_from_name
from lerppu.inference.vendor import canonicalize_vendor
from lerppu.models import ConnectionType, MediaType, Product

log = logging.getLogger(__name__)


def massage_jimms(
    prod: dict,
    media_type: MediaType,
    connection_type: ConnectionType,
) -> Product:
    name = f"{prod['VendorName']} {prod['Name']}"
    return Product(
        media_type=media_type,
        connection_type=connection_type,
        id=f"jimms:{prod['ProductID']}",
        source="jimms",
        name=name,
        size_mb=get_mb_size_from_name(name),
        original_price=prod["OvhPriceTax"],  # TODO: not exactly the original price
        current_price=prod["PriceTax"],
        url=f"https://www.jimms.fi/fi/{prod['Uri']}",
        vendor_sku=prod["Code"],
        manufacturer=canonicalize_vendor(prod["VendorName"]),
        _original=prod,
    )


def get_category_products(
    cli: httpx.Client,
    *,
    category_id: str,
    media_type: MediaType,
    connection_type: ConnectionType,
) -> Iterable[Product]:
    for page_no in count(1):
        log.info(f"Fetching page {page_no} of category {category_id}")
        resp = cli.post(
            url=f"https://www.jimms.fi/api/product/list/{category_id}",
            headers={
                "apikey": "public",
                "referrer": "https://www.jimms.fi/",
            },
            json={
                "Page": page_no,
                "Items": 50,
                "OrderBy": "5",
                "OrderDir": "1",
                "Filters": {
                    "SearchQuery": "",
                    "MinPrice": 0,
                    "MaxPrice": 0,
                    "Vendors": [],
                    "Groups": [],
                },
            },
        )
        resp.raise_for_status()
        data = resp.json()
        products = data.get("Products")
        if not products:
            break
        for prod in products:
            yield massage_jimms(
                prod,
                media_type=media_type,
                connection_type=connection_type,
            )
