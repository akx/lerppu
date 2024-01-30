import logging

from lerppu.models import Product

log = logging.getLogger(__name__)


def validate_product(product: Product) -> bool:
    if not product.size_mb:
        log.warning(f"No size for {product.id}")
        return False

    if product.id.startswith("proshop:") and product.id.endswith("d"):
        log.warning(f"Skipping demo product {product.id}")
        return False

    if "*DEMO*" in product.name:
        log.warning(f"Skipping demo product {product.id}")
        return False

    return True
