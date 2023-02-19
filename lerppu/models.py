import dataclasses


@dataclasses.dataclass
class Product:
    id: str
    name: str
    original_price: float | None
    current_price: float
    url: str
    source: str
    _original: dict
    vendor_sku: str
    manufacturer: str
    size_mb: int | None
