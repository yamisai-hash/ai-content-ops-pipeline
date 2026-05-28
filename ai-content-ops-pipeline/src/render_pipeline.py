"""
render_pipeline.py — assemble a vertical short-form video.

Representative wrapper around the real toolchain (FFmpeg render + local TTS +
caption overlay). The production version times captions to TTS word boundaries
and renders 1080x1920; here we build the FFmpeg command and return a descriptor
so the *shape* is reviewable without shipping large binaries or invoking FFmpeg.
"""
from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class RenderSpec:
    resolution: str = "1080x1920"
    fps: int = 30
    tts_provider: str = "edge_tts"      # local; paid provider optional behind a flag
    music_gain: float = 0.14


@dataclass
class Asset:
    asset_id: str
    format: str
    path: str
    caption: str
    spec: RenderSpec = field(default_factory=RenderSpec)
    meta: Dict[str, Any] = field(default_factory=dict)


def _ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def build_ffmpeg_cmd(bg_clip: str, voiceover: str, subtitles: str,
                     out_path: str, spec: RenderSpec) -> List[str]:
    """Return the FFmpeg argv that would render the reel (not executed here)."""
    w, h = spec.resolution.split("x")
    return [
        "ffmpeg", "-y", "-i", bg_clip, "-i", voiceover,
        "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,"
               f"crop={w}:{h},subtitles={subtitles}",
        "-r", str(spec.fps), "-c:v", "libx264", "-c:a", "aac",
        "-shortest", out_path,
    ]


def render_reel(idea: Dict[str, Any], spec: RenderSpec = None) -> Asset:
    """Produce an Asset descriptor for a reel built from an idea.

    In the showcase we don't execute FFmpeg; we record the command + spec so the
    pipeline is inspectable. ``meta.rendered`` reflects whether FFmpeg is present.
    """
    spec = spec or RenderSpec()
    asset_id = f"C-{abs(hash(idea.get('hook',''))) % 9000 + 1000}"
    cmd = build_ffmpeg_cmd("backgrounds/clip.mp4", "tts/voiceover.wav",
                           "subtitles/captions.ass", f"out/{asset_id}.mp4", spec)
    return Asset(
        asset_id=asset_id,
        format=idea.get("format", "reel"),
        path=f"out/{asset_id}.mp4",
        caption=idea.get("caption", ""),
        spec=spec,
        meta={"ffmpeg_cmd": cmd, "rendered": _ffmpeg_available(), "source": idea.get("source")},
    )
