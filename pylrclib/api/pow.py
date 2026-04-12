from __future__ import annotations

import hashlib

from ..exceptions import PoWError


def solve_pow(prefix: str, target_hex: str) -> str:
    if not prefix or not target_hex:
        raise PoWError(f"invalid PoW params: prefix={prefix!r}, target={target_hex!r}")
    target = int(target_hex, 16)
    nonce = 0
    while True:
        digest = hashlib.sha256(f"{prefix}{nonce}".encode("utf-8")).hexdigest()
        if int(digest, 16) <= target:
            return str(nonce)
        nonce += 1
