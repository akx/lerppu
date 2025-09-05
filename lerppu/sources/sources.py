from collections.abc import Iterable

import httpx

from lerppu.sources.base import ProductSource
from lerppu.sources.datablocks import get_datablocks_sources
from lerppu.sources.dustinhome import get_dustinhome_sources
from lerppu.sources.jimms import get_jimms_sources
from lerppu.sources.verk import get_verk_sources


def get_sources(sess: httpx.Client) -> Iterable[ProductSource]:
    yield from get_verk_sources(sess)
    yield from get_jimms_sources(sess)
    # yield from get_proshop_sources(sess)
    yield from get_dustinhome_sources(sess)
    yield from get_datablocks_sources(sess)
