import logging
from collections.abc import Iterable
from itertools import count

import httpx

from lerppu.inference.size import get_mb_size_from_name
from lerppu.inference.vendor import canonicalize_vendor
from lerppu.models import ConnectionType, MediaType, Product
from lerppu.sources.base import ProductSource

log = logging.getLogger(__name__)


def massage_verk(
    prod: dict,
    *,
    media_type: MediaType,
    connection_type: ConnectionType,
) -> Product:
    vendor_sku = mpns[0] if (mpns := prod.get("mpns", [])) else ""
    manufacturer = canonicalize_vendor(prod.get("brand", {}).get("name") or "")
    pid = prod["pid"]
    return Product(
        media_type=media_type,
        connection_type=connection_type,
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


def get_category_products(
    cli: httpx.Client,
    *,
    base_filter: str,
    media_type: MediaType,
    connection_type: ConnectionType,
) -> Iterable[Product]:
    for page_no in count(0):
        log.info(f"Fetching page {page_no + 1} of filter {base_filter}")
        resp = cli.get(
            url="https://web-api.service.verkkokauppa.com/search",
            params={
                "pageNo": page_no,
                "pageSize": "48",
                "sort": "score:desc",
                "lang": "fi",
                "baseFilter": base_filter,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        products = data.get("products")
        if not products:
            break
        for prod in products:
            yield massage_verk(
                prod,
                media_type=media_type,
                connection_type=connection_type,
            )


def get_verk_sources(sess: httpx.Client) -> Iterable[ProductSource]:
    yield ProductSource(
        name="Verkkis HDDs",
        generator=get_category_products(
            sess,
            base_filter="category:hard_disk_drives",
            connection_type=ConnectionType.SATA,
            media_type=MediaType.HDD,
        ),
    )
    yield ProductSource(
        name="Verkkis SSDs",
        generator=get_category_products(
            sess,
            base_filter="category:ssd_drives",
            connection_type=ConnectionType.SATA,
            media_type=MediaType.SSD,
        ),
    )
    yield ProductSource(
        name="Verkkis M2s",
        generator=get_category_products(
            sess,
            base_filter="category:m2_ssd",
            connection_type=ConnectionType.M2,
            media_type=MediaType.SSD,
        ),
    )
