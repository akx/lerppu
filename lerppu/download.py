import logging

import diskcache
import httpx

from lerppu.caching_http_transport import CachingHTTPTransport
from lerppu.models import Product
from lerppu.sources.sources import get_sources
from lerppu.validation import validate_product

log = logging.getLogger(__name__)


def download_product_info(*, use_cache: bool) -> tuple[list[Product], list[str]]:
    log.info("Downloading information...")
    transport = (
        CachingHTTPTransport(cache=diskcache.Cache("./cache", disk_min_file_size=1048576)) if use_cache else None
    )
    headers = {
        "User-Agent": f"{httpx._client.USER_AGENT} (+https://akx.github.io/lerppu/)",
    }
    products = []
    warnings = []
    with httpx.Client(transport=transport, headers=headers) as sess:
        for source in get_sources(sess):
            log.info(f"Downloading {source.name}...")
            n_valid = 0
            n_invalid = 0
            try:
                for prod in source.generator:
                    if validate_product(prod):
                        n_valid += 1
                        products.append(prod)
                    else:
                        n_invalid += 1
            except httpx.HTTPError as e:
                log.warning("HTTP error while fetching %s: %s", source.name, e, exc_info=True)
                warnings.append(f"HTTP error while fetching {source.name}: {e}")
            if n_valid == 0:
                log.warning("No valid products found in %s", source.name)
                warnings.append(f"No valid products found in {source.name}")
            log.info("%s: %d valid, %d invalid", source.name, n_valid, n_invalid)
    return products, warnings
