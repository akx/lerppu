import logging
from collections.abc import Iterable

import httpx

from lerppu.inference.size import get_mb_size_from_name
from lerppu.inference.type import get_connection_type_from_data, get_media_type_from_data
from lerppu.inference.vendor import canonicalize_vendor
from lerppu.models import MediaType, Product

log = logging.getLogger(__name__)


def massage_datablocks(prod: dict) -> Product | None:
    name = prod["title"]

    data = [*prod.get("tags", []), name, prod.get("product_type", "")]
    connection_type = get_connection_type_from_data(data)
    media_type = get_media_type_from_data(data) or MediaType.UNKNOWN

    variants = prod.get("variants", [])
    price_data_source = variants[0] if variants else prod
    current_price = float(price_data_source.get("price", 0))
    original_price = float(price_data_source.get("compare_at_price") or current_price)
    sku = price_data_source.get("sku", "")
    if not price_data_source.get("available"):
        return None

    return Product(
        media_type=MediaType(media_type),
        connection_type=connection_type,
        id=f"datablocks:{prod['id']}",
        source="datablocks",
        name=name.replace("White Label Hard Drive", "WLBL HDD"),
        size_mb=get_mb_size_from_name(name),
        original_price=original_price,
        current_price=current_price,
        url=f"https://datablocks.dev/products/{prod['handle']}",
        vendor_sku=sku,
        manufacturer=canonicalize_vendor(prod.get("vendor", "")),
        status="refurb",
        _original=prod,
    )


def get_products(cli: httpx.Client) -> Iterable[Product]:
    log.info("Fetching products from Datablocks")
    resp = cli.get("https://datablocks.dev/products.json/?limit=250")
    resp.raise_for_status()
    data = resp.json()
    products = data.get("products", [])
    log.info(f"Found {len(products)} products from Datablocks")
    for prod in products:
        if p := massage_datablocks(prod):
            yield p
