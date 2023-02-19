import re

sku_regexps = [
    re.compile(r"ST\d+\w+"),  # Seagate, eg. ST2000DM008
    re.compile(r"HU[CSH]\w+"),  # HGST, eg. HUS726T6TALE6L4
    re.compile(r"(MG|HDW)\w{6,}"),  # Some Toshiba SKUs, e.g. MG04ACA400E, HDWJ105UZSVA
]


def infer_sku_from_name(name: str) -> str | None:
    for regexp in sku_regexps:
        match = regexp.search(name)
        if match:
            return match.group(0)
    return None
