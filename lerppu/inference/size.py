import re
from typing import Optional

size_re = re.compile(r"(?P<num>\d+)\s*(?P<unit>[tgm])[bt]?[\s,]", flags=re.I)

multipliers = {
    "t": 1024 * 1024,
    "g": 1024,
    "m": 1,
}


def get_mb_size_from_name(name: str) -> Optional[int]:
    match = size_re.search(name)
    if not match:
        return None
    num = int(match.group("num"))
    mult = multipliers[match.group("unit").lower()]
    return int(num * mult)
