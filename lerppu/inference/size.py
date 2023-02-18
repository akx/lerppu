import re

size_re = re.compile(
    r"(?P<num>[0-9][0-9,.]*)\s*(?P<unit>[tgm])[bt]?([\s,]|$)", flags=re.I
)

multipliers = {
    "t": 1024 * 1024,
    "g": 1024,
    "m": 1,
}


def get_mb_size_from_name(name: str) -> Optional[int]:
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
        sizes_found.add(size)
    if sizes_found:
        return max(sizes_found)
    return None
