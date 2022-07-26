import logging
from typing import Iterable

from lerppu.models import Product

log = logging.getLogger(__name__)


def validate_products(products: Iterable[Product]) -> Iterable[Product]:
    for prod in products:
        if not prod.size_mb:
            log.warning(f"No size for {prod.id}")
            continue
        if (prod.id.startswith("proshop:") and prod.id.endswith("d")) or "*DEMO*" in prod.name:
            log.warning(f"Skipping demo product {prod.id}")
            continue
        yield prod
