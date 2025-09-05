import dataclasses
from collections.abc import Iterable

from lerppu.models import Product


@dataclasses.dataclass
class ProductSource:
    name: str
    generator: Iterable[Product]
