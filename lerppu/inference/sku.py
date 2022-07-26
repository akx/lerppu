import re
from typing import Optional

sku_regexps = [
    re.compile(r"ST\d+\w+"),  # Seagate, eg. ST2000DM008
    re.compile(r"HUS\w+"),  # HGST, eg. HUS726T6TALE6L4
]


def infer_sku_from_name(name: str) -> Optional[str]:
    for regexp in sku_regexps:
        match = regexp.search(name)
        if match:
            return match.group(0)
    return None
