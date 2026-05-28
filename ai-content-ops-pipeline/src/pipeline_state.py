"""
pipeline_state.py — the filesystem *is* the state machine.

Content physically moves through numbered stage folders. The stage of any asset
is therefore unambiguous and crash-recoverable — no database required. This
module just formalizes the transitions and validates that moves are legal.
"""
from __future__ import annotations

import os
import shutil
from typing import List

# Ordered pipeline stages (folder names in the real tree).
STAGES: List[str] = [
    "01_RAW_FOOTAGE",
    "05_READY_TO_EDIT",
    "06_FINISHED_VIDEOS",
    "07_READY_TO_POST",
    "08_POSTED",
    "09_ANALYTICS",
]


def next_stage(current: str) -> str:
    """Return the stage that legally follows ``current``."""
    i = STAGES.index(current)
    if i + 1 >= len(STAGES):
        raise ValueError(f"{current} is the final stage")
    return STAGES[i + 1]


def is_legal_transition(src: str, dst: str) -> bool:
    """Only forward, one step at a time."""
    try:
        return STAGES.index(dst) == STAGES.index(src) + 1
    except ValueError:
        return False


def advance(root: str, filename: str, src: str, dst: str) -> str:
    """Move an asset one stage forward; raise on illegal transition.

    Protected folders are never deleted — this only *moves* files forward.
    """
    if not is_legal_transition(src, dst):
        raise ValueError(f"illegal transition {src} -> {dst}")
    src_path = os.path.join(root, src, filename)
    dst_dir = os.path.join(root, dst)
    os.makedirs(dst_dir, exist_ok=True)
    shutil.move(src_path, os.path.join(dst_dir, filename))
    return os.path.join(dst, filename)
