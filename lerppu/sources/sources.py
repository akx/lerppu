import dataclasses
from collections.abc import Iterable

import httpx

from lerppu.models import ConnectionType, MediaType, Product
from lerppu.sources import dustinhome, jimms, proshop, verk


@dataclasses.dataclass
class ProductSource:
    name: str
    generator: Iterable[Product]


def get_sources(sess: httpx.Client) -> Iterable[ProductSource]:
    yield from get_verk_sources(sess)
    yield from get_jimms_sources(sess)
    # yield from get_proshop_sources(sess)
    yield from get_dustinhome_sources(sess)


def get_verk_sources(sess: httpx.Client) -> Iterable[ProductSource]:
    yield ProductSource(
        name="Verkkis HDDs",
        generator=verk.get_category_products(
            sess,
            base_filter="category:hard_disk_drives",
            connection_type=ConnectionType.SATA,
            media_type=MediaType.HDD,
        ),
    )
    yield ProductSource(
        name="Verkkis SSDs",
        generator=verk.get_category_products(
            sess,
            base_filter="category:ssd_drives",
            connection_type=ConnectionType.SATA,
            media_type=MediaType.SSD,
        ),
    )
    yield ProductSource(
        name="Verkkis M2s",
        generator=verk.get_category_products(
            sess,
            base_filter="category:m2_ssd",
            connection_type=ConnectionType.M2,
            media_type=MediaType.SSD,
        ),
    )


def get_jimms_sources(sess: httpx.Client) -> Iterable[ProductSource]:
    yield ProductSource(
        name="Jimms SATA",
        generator=jimms.get_category_products(
            sess,
            category_id="000-0MU",
            connection_type=ConnectionType.SATA,
            media_type=MediaType.HDD,
        ),
    )
    yield ProductSource(
        name="Jimms SSD",
        generator=jimms.get_category_products(
            sess,
            category_id="000-0EE",
            connection_type=ConnectionType.SATA,
            media_type=MediaType.SSD,
        ),
    )
    yield ProductSource(
        name="Jimms M.2",
        generator=jimms.get_category_products(
            sess,
            category_id="000-1AR",
            connection_type=ConnectionType.M2,
            media_type=MediaType.SSD,
        ),
    )


def get_proshop_sources(sess: httpx.Client) -> Iterable[ProductSource]:
    yield ProductSource(
        name="Proshop HDD",
        generator=proshop.get_category_products(
            sess,
            category_id="Kovalevy",
            media_type=MediaType.HDD,
        ),
    )
    yield ProductSource(
        name="Proshop SSD",
        generator=proshop.get_category_products(
            sess,
            category_id="SSD",
            media_type=MediaType.SSD,
        ),
    )


def get_dustinhome_sources(sess: httpx.Client) -> Iterable[ProductSource]:
    yield ProductSource(
        name="Dustinhome HDD",
        generator=dustinhome.get_category_products(
            sess,
            category_id="2030994",
            media_type=MediaType.HDD,
        ),
    )
    yield ProductSource(
        name="Dustinhome SSD",
        generator=dustinhome.get_category_products(
            sess,
            category_id="2032014",
            media_type=MediaType.SSD,
        ),
    )
