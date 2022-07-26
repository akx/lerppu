import logging
from typing import Iterable

from lerppu.models import Product

log = logging.getLogger(__name__)


def validate_products(products: Iterable[Product]) -> Iterable[Product]:
    for prod in products:
        if not prod.size_mb:
            log.warning(f"No size for {prod.id}")
            continue
        yield prod
