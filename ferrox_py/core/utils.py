from typing import Any


def to_str(val: Any) -> str:
    if isinstance(val, bytes):
        return val.decode("utf-8")
    return str(val) if val is not None else ""
