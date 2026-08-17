"""
serialization.py — NumPy-aware JSON serialization helpers.

All internal computations use ``np.float64``; these helpers recursively
convert NumPy scalar and array types to native Python types before JSON
serialization.
"""

from __future__ import annotations

import json
from typing import Any

import numpy as np


def sanitize_numpy(obj: Any) -> Any:
    """Recursively convert NumPy types to native Python types."""
    if isinstance(obj, dict):
        return {key: sanitize_numpy(value) for key, value in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [sanitize_numpy(value) for value in obj]
    if isinstance(obj, np.ndarray):
        return [sanitize_numpy(value) for value in obj.tolist()]
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.complexfloating):
        return complex(obj)
    return obj


class NumpyJSONEncoder(json.JSONEncoder):
    """JSON encoder falling back to ``sanitize_numpy`` for unknown types."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, (np.integer, np.floating, np.bool_, np.ndarray)):
            return sanitize_numpy(obj)
        return super().default(obj)
