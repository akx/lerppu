import logging
from itertools import count
from typing import Iterable

import httpx

from lerppu.inference.size import get_mb_size_from_name
from lerppu.inference.vendor import canonicalize_vendor
from lerppu.models import Product


log = logging.getLogger(__name__)


def massage_verk(prod: dict) -> Product:
    vendor_sku = mpns[0] if (mpns := prod.get("mpns", [])) else ""
    manufacturer = canonicalize_vendor(prod.get("brand", {}).get("name") or "")
    pid = prod["pid"]
    return Product(
        id=f"verk:{pid}",
        source="verkkokauppa",
        name=(prod["name"]),
        size_mb=get_mb_size_from_name(prod["name"]),
        original_price=prod["price"]["original"],
        current_price=prod["price"]["current"],
        url=f"https://verk.com/{pid}",
        vendor_sku=vendor_sku,
        manufacturer=manufacturer,
        _original=prod,
    )


def get_category_products(cli: httpx.Client, *, category_id: str) -> Iterable[Product]:
    for page_no in count(0):
        log.info(f"Fetching page {page_no + 1} of category {category_id}")
        resp = cli.get(
            url="https://web-api.service.verkkokauppa.com/search",
            params={
                "pageNo": page_no,
                "pageSize": "48",
                "sort": "popularity:desc",
                "lang": "fi",
                "context": "category_page",
                "contextFilter": category_id,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        products = data.get("products")
        if not products:
            break
        for prod in products:
            yield massage_verk(prod)
