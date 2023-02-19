from __future__ import annotations

import logging
import re
from collections.abc import Iterable
from typing import TypeVar

from lerppu.models import ConnectionType

log = logging.getLogger(__name__)

T = TypeVar("T")

connection_smells = {
    ConnectionType.M2: re.compile(r"M.2\b", re.IGNORECASE),
    ConnectionType.PCIE: re.compile(
        r"(2.5\"|HHHL)[\s,]+(PCI\s*e)|PCIe-kortti|SFF, PCI|PCI Express [23].0 x\d",
        re.IGNORECASE,
    ),
    ConnectionType.SAS: re.compile(
        r"SAS[- ]*[1236,]|Serial Attached SCSI", re.IGNORECASE
    ),
    ConnectionType.SATA: re.compile(
        r"SATA\s*[36]Gb|S(erial )?ATA-(600|150|300)|2.5\" SATA|ATA SSD|SATA$",
        re.IGNORECASE,
    ),
    ConnectionType.THUNDERBOLT: re.compile(r"Thunderbolt", re.IGNORECASE),
    ConnectionType.U2: re.compile(r"U.2\b", re.IGNORECASE),
    ConnectionType.U3: re.compile(r"U.3\b", re.IGNORECASE),
    ConnectionType.USB: re.compile(r"USB", re.IGNORECASE),
}


def _find_smells(
    strings: Iterable[str | None], smell_map: dict[T, re.Pattern]
) -> set[T]:
    smells = set()
    for s in strings:
        if not s:
            continue
        for smell, smell_re in smell_map.items():
            if smell_re.search(s):
                smells.add(smell)
    return smells


def get_connection_type_from_data(values: list[str | None]) -> ConnectionType | None:
    try:
        smells = _find_smells(values, connection_smells)
        if ConnectionType.SAS in smells:  # Anything that smells SAS is SAS
            return ConnectionType.SAS
        if ConnectionType.M2 in smells:  # Anything that smells M.2 is M.2
            return ConnectionType.M2
        if len(smells) != 1:
            raise ValueError(f"Too many or too few smells: {smells}")
        return ConnectionType(next(iter(smells)))
    except Exception as exc:
        log.warning(
            "Can't get connection type for %r: %s",
            values,
            exc,
        )
    return None
