import logging

log = logging.getLogger(__name__)

known_vendors = {
    "a-data": "A-Data",
    "corsair": "Corsair",
    "crucial": "Crucial",
    "dell": "Dell",
    "fujitsu": "Fujitsu",
    "gigabyte": "Gigabyte",
    "goodram": "Goodram",
    "hewlett packard enterprise": "HPE",
    "hgst": "HGST",
    "ibm": "IBM",
    "intel": "Intel",
    "intenso": "Intenso",
    "kingston": "Kingston",
    "kioxia": "Kioxia",
    "lenovo": "Lenovo",
    "lexar": "Lexar",
    "patriot": "Patriot",
    "pny": "PNY",
    "samsung": "Samsung",
    "sandisk": "Sandisk",
    "seagate": "Seagate",
    "silicon power": "Silicon Power",
    "toshiba": "Toshiba",
    "transcend": "Transcend",
    "verbatim": "Verbatim",
    "wd": "Western Digital",
    "western digital": "Western Digital",
}


def infer_vendor_from_name(name: str) -> str | None:
    name = name.lower()
    for moniker, canonical in known_vendors.items():
        if moniker in name:
            return canonical
    if name.startswith("hp"):
        return "HP"
    log.warning(f"Could not infer vendor from name: {name}")
    return None


def canonicalize_vendor(vendor: str) -> str:
    vendor = known_vendors.get(vendor.lower(), vendor)
    vendor = vendor.replace(", Inc.", "")
    return vendor
