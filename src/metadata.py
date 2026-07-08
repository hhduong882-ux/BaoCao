import json
import subprocess
from pathlib import Path
from typing import Optional


def _parse_fps(fps_str: Optional[str]) -> Optional[float]:
    if not fps_str:
        return None
    if "/" in fps_str:
        num, denom = fps_str.split("/", 1)
        try:
            return float(num) / float(denom)
        except (TypeError, ValueError, ZeroDivisionError):
            return None
    try:
        return float(fps_str)
    except (TypeError, ValueError):
        return None


def extract_metadata(video_path: Path, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata_file = output_dir / "metadata.json"

    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-of",
        "json",
        "-show_format",
        "-show_streams",
        str(video_path),
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Khong the trich xuat metadata: {result.stderr.strip()}")

    raw_metadata = json.loads(result.stdout)
    format_info = raw_metadata.get("format", {})
    video_stream = next(
        (s for s in raw_metadata.get("streams", []) if s.get("codec_type") == "video"),
        None,
    )
    if video_stream is None:
        raise ValueError("Video khong co stream video")
    
    tags = format_info.get("tags", {})
    encoder = tags.get("encoder", "Unknown") if tags else "Unknown"

    metadata = {
        "container": {
            "duration": float(format_info.get("duration", 0) or 0),
            "overall_bitrate": int(format_info.get("bit_rate")) if format_info.get("bit_rate") else None,
            "encoder": encoder
        },
        "video_stream": {
            "codec": video_stream.get("codec_name"),
            "fps_r": _parse_fps(video_stream.get("r_frame_rate")),
            "time_base": video_stream.get("time_base"),
        },
    }

    with open(metadata_file, "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=4, ensure_ascii=False)

    return metadata_file
