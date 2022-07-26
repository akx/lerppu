import dataclasses
from typing import Optional


@dataclasses.dataclass
class Product:
    id: str
    name: str
    original_price: Optional[float]
    current_price: float
    url: str
    source: str
    _original: dict
    vendor_sku: str
    manufacturer: str
    size_mb: Optional[int]
