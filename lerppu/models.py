import dataclasses
from enum import Enum


class MediaType(Enum):
    HDD = "hdd"
    SSD = "ssd"
    UNKNOWN = "unknown"


class ConnectionType(Enum):
    M2 = "m2"
    MSATA = "msata"
    PCIE = "pcie"
    SAS = "sas"
    SATA = "sata"
    THUNDERBOLT = "thunderbolt"
    U2 = "u2"
    U3 = "u3"
    UNKNOWN = "unknown"
    USB = "usb"


@dataclasses.dataclass(frozen=True)
class Product:
    media_type: MediaType
    connection_type: ConnectionType
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
    status: str = ""
