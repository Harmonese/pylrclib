from __future__ import annotations

import hashlib

from ..exceptions import PoWError


_MAX_POW_NONCE = 2_000_000


def solve_pow(prefix: str, target_hex: str) -> str:
    if not prefix or not target_hex:
        raise PoWError(f"invalid PoW params: prefix={prefix!r}, target={target_hex!r}")
    target = int(target_hex, 16)
    for nonce in range(_MAX_POW_NONCE):
        digest = hashlib.sha256(f"{prefix}{nonce}".encode("utf-8")).hexdigest()
        if int(digest, 16) <= target:
            return str(nonce)
    raise PoWError(f"PoW not solved within {_MAX_POW_NONCE} iterations")
