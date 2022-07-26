import logging
from typing import Optional

log = logging.getLogger(__name__)

known_vendors = {
    "dell": "Dell",
    "hgst": "HGST",
    "seagate": "Seagate",
    "toshiba": "Toshiba",
    "wd": "Western Digital",
    "western digital": "Western Digital",
    "fujitsu": "Fujitsu",
    "lenovo": "Lenovo",
}


def infer_vendor_from_name(name: str) -> Optional[str]:
    name = name.lower()
    for moniker, canonical in known_vendors.items():
        if moniker in name:
            return canonical
    if name.startswith("hp"):
        return "HP"
    log.warning(f"Could not infer vendor from name: {name}")
    return None


def canonicalize_vendor(vendor: str) -> str:
    return known_vendors.get(vendor.lower(), vendor)
