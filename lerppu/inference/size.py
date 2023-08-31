import logging
import re

log = logging.getLogger(__name__)

size_re = re.compile(
    r"\b(?P<num>[0-9][0-9,.]*)\s*(?P<unit>[tgm])[bt]?([\s,]|$)", flags=re.I
)

multipliers = {
    "t": 1024 * 1024,
    "g": 1024,
    "m": 1,
}

MAX_LIKELY_MB_SIZE = 200 * multipliers["t"]  # 200 TB


def get_mb_size_from_name(name: str) -> int | None:
    """
    >>> get_mb_size_from_name('Kingston DC500M 1,92 Tt SATA III 2,5" SSD-levy')
    2013265
    >>> get_mb_size_from_name('Kingston Data Centre DC500M SSD - 480GB')
    491520
    """
    sizes_found = set()

    for match in size_re.finditer(name):
        if not match:
            return None
        num = float(match.group("num").replace(",", "."))
        mult = multipliers[match.group("unit").lower()]
        size = int(num * mult)
        if size >= MAX_LIKELY_MB_SIZE:
            log.warning("Likely invalid size %s in %s", size, name)
            continue
        sizes_found.add(size)
    if sizes_found:
        return max(sizes_found)
    return None
