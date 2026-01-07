import logging
import uuid
from collections.abc import Iterable
from itertools import count

import httpx

from lerppu.inference.size import get_mb_size_from_name
from lerppu.inference.vendor import infer_vendor_from_name
from lerppu.models import ConnectionType, MediaType, Product
from lerppu.sources.base import ProductSource

log = logging.getLogger(__name__)


def massage_verk(
    prod: dict,
    *,
    media_type: MediaType,
    connection_type: ConnectionType,
) -> Product:
    attrs = prod["attributes"]
    pid = prod["id"]
    name = attrs["name"]
    manufacturer = infer_vendor_from_name(name)
    # vendor_sku = mpns[0] if (mpns := prod.get("mpns", [])) else ""
    # manufacturer = canonicalize_vendor(prod.get("brand", {}).get("name") or "")
    return Product(
        media_type=media_type,
        connection_type=connection_type,
        id=f"verk:{pid}",
        source="verkkokauppa",
        name=name,
        size_mb=get_mb_size_from_name(name),
        original_price=attrs["price"]["original"],
        current_price=attrs["price"]["current"],
        url=f"https://verk.com/{pid}",
        vendor_sku="",  # Not available in search data anymore
        manufacturer=manufacturer,
        _original=prod,
    )


def get_category_products(
    cli: httpx.Client,
    *,
    category_filter: str,
    media_type: MediaType,
    connection_type: ConnectionType,
) -> Iterable[Product]:
    session_id = str(uuid.uuid7())
    for page_no in count(0):
        log.info(f"Fetching page {page_no + 1} of filter {category_filter}")
        resp = cli.get(
            url="https://search.service.verkkokauppa.com/fi/api/v1/product-search",
            params={
                "filter[base+category][]": [category_filter],
                "page[number]": page_no + 1,
                "page[size]": "48",
                "sort": "-releaseDate",
                "sessionId": session_id,
                "private": "true",
                "include": "campaigns,category,salesCategories.parent,facets",
            },
        )
        resp.raise_for_status()
        data = resp.json()
        products = [p for p in data.get("data") if p["type"] == "products"]
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
            category_filter="hard_disk_drives",
            connection_type=ConnectionType.SATA,
            media_type=MediaType.HDD,
        ),
    )
    yield ProductSource(
        name="Verkkis SSDs",
        generator=get_category_products(
            sess,
            category_filter="ssd_drives",
            connection_type=ConnectionType.SATA,
            media_type=MediaType.SSD,
        ),
    )
    yield ProductSource(
        name="Verkkis M2s",
        generator=get_category_products(
            sess,
            category_filter="m2_ssd",
            connection_type=ConnectionType.M2,
            media_type=MediaType.SSD,
        ),
    )
