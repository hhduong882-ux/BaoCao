import csv
import json
import math
import subprocess
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

def _safe_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _run_ffprobe(video_path: str) -> Dict[str, Any]:
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_frames",
        "-show_entries",
        "frame=best_effort_timestamp_time,pkt_dts_time,pkt_duration_time,pkt_size,pict_type,key_frame",
        "-of", "json",
        video_path,
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Khong the trich xuat du lieu ffprobe: {result.stderr.strip()}")

    return json.loads(result.stdout)


def _build_timed_units_from_frames(
    raw_frames: List[Dict[str, Any]],
    duration: float,
    fps: Optional[float],
):
    units: List[Tuple[float, float, float]] = []

    for frame in raw_frames:
        frame_time = _safe_float(frame.get("best_effort_timestamp_time"))
        if frame_time is None:
            frame_time = _safe_float(frame.get("pkt_dts_time"))

        frame_size = _safe_float(frame.get("pkt_size"))

        if frame_time is None or frame_size is None:
            continue
        if frame_size < 0:
            continue

        frame_duration = _safe_float(frame.get("pkt_duration_time")) or 0.0
        units.append((frame_time, frame_size, frame_duration))

    if not units:
        return units

    units.sort(key=lambda x: x[0])
    default_duration = (1.0 / fps) if fps and fps > 0 else 0.04

    for idx, unit in enumerate(units):
        unit_time, unit_size, unit_duration = unit

        if unit_duration <= 0:
            if idx + 1 < len(units):
                unit_duration = max(0.0, units[idx + 1][0] - unit_time)
            else:
                unit_duration = max(0.0, duration - unit_time)

        if unit_duration <= 0:
            unit_duration = default_duration

        units[idx] = (unit_time, unit_size, unit_duration)

    return units


def _build_gop_series(
    raw_frames: List[Dict[str, Any]],
    duration: float,
) -> List[Dict[str, Any]]:
    frames: List[Dict[str, Any]] = []

    for frame in raw_frames:
        frame_time = _safe_float(frame.get("best_effort_timestamp_time"))
        if frame_time is None:
            frame_time = _safe_float(frame.get("pkt_dts_time"))
        if frame_time is None:
            continue

        frame_size = _safe_float(frame.get("pkt_size"))
        frame_duration = _safe_float(frame.get("pkt_duration_time")) or 0.0
        pict_type = str(frame.get("pict_type") or "").upper()
        is_key = int(frame.get("key_frame") or 0) == 1 or pict_type == "I"

        frames.append(
            {
                "time": frame_time,
                "size": max(0.0, frame_size or 0.0),
                "duration": frame_duration,
                "pict_type": pict_type,
                "is_key": is_key,
            }
        )

    if not frames:
        return []

    frames.sort(key=lambda x: x["time"])

    for idx, frame in enumerate(frames):
        if frame["duration"] > 0:
            continue
        if idx + 1 < len(frames):
            frame["duration"] = max(0.0, frames[idx + 1]["time"] - frame["time"])
        else:
            frame["duration"] = max(0.0, duration - frame["time"])
        if frame["duration"] <= 0:
            frame["duration"] = 0.04

    gop_rows: List[Dict[str, Any]] = []
    previous_start: Optional[float] = None
    gop_idx = 1
    start_idx = 0
    frame_count = len(frames)

    for idx in range(1, frame_count + 1):
        is_gop_boundary = (idx == frame_count or frames[idx]["is_key"])
        if not is_gop_boundary:
            continue

        end_idx = idx
        if end_idx <= start_idx:
            continue

        start_time = frames[start_idx]["time"]
        if end_idx < frame_count:
            end_time = frames[end_idx]["time"]
        else:
                end_time = duration

        gop_duration = max(0.0, end_time - start_time)
        total_bits = sum(frames[i]["size"] * 8.0 for i in range(start_idx, end_idx))
        bitrate_bps = total_bits / gop_duration if gop_duration > 0 else 0.0

        i_count = sum(1 for i in range(start_idx, end_idx) if frames[i]["pict_type"] == "I")
        p_count = sum(1 for i in range(start_idx, end_idx) if frames[i]["pict_type"] == "P")
        b_count = sum(1 for i in range(start_idx, end_idx) if frames[i]["pict_type"] == "B")
        key_count = sum(1 for i in range(start_idx, end_idx) if frames[i]["is_key"])
        keyframe_interval = (start_time - previous_start) if previous_start is not None else ""

        gop_rows.append(
            {
                "gop": gop_idx,
                "start(s)": round(start_time, 3),
                "end(s)": round(end_time, 3),
                "duration(s)": round(gop_duration, 3),
                "frames": end_idx - start_idx,
                "keyframes": key_count,
                "i_frames": i_count,
                "p_frames": p_count,
                "b_frames": b_count,
                "bitrate(kbps)": f"{bitrate_bps / 1000.0:.3f}",
                "keyframe_interval(s)": (
                    f"{keyframe_interval:.3f}" if keyframe_interval != "" else ""
                ),
            }
        )
        previous_start = start_time
        start_idx = end_idx
        gop_idx += 1

    return gop_rows


def _accumulate_bits_by_segment(
    units: List[Tuple[float, float, float]],
    duration: float,
    segment_duration: float,
) -> List[float]:
    
    segment_count = int(math.ceil(duration / segment_duration))
    segment_bits = [0.0] * segment_count
    seg_dur = segment_duration
    dur = duration
    eps = 1e-12

    for unit in units:
        unit_start, unit_size, unit_duration = unit
        unit_end = unit_start + unit_duration

        clipped_start = max(0.0, unit_start)
        clipped_end = min(dur, unit_end)
        clipped_duration = clipped_end - clipped_start

        if clipped_duration <= 0:
            continue

        unit_bits = unit_size * 8.0

        first_seg = int(clipped_start // seg_dur)
        last_seg = min(int((clipped_end - eps) // seg_dur), segment_count - 1)

        if first_seg == last_seg:
            segment_bits[first_seg] += unit_bits
            continue

        for seg_idx in range(first_seg, last_seg + 1):
            seg_start = seg_idx * seg_dur
            seg_end = min(seg_start + seg_dur, dur)

            overlap = min(clipped_end, seg_end) - max(clipped_start, seg_start)
            if overlap > 0:
                segment_bits[seg_idx] += unit_bits * (overlap / clipped_duration)

    return segment_bits


def extract_segment_bitrate(video_path: Path, step: float, output_dir: Path):
    if step <= 0:
        raise ValueError("step phai lon hon 0")

    metadata_path = output_dir / "metadata.json"
    with open(metadata_path, "r", encoding="utf-8") as file:
        metadata = json.load(file)

    duration = _safe_float(metadata.get("container", {}).get("duration")) or 0.0
    overall_bitrate = _safe_float(metadata.get("container", {}).get("overall_bitrate")) or 0.0
    fps = _safe_float(metadata.get("video_stream", {}).get("fps_r"))
    
    ffprobe_frames = _run_ffprobe(str(video_path))
    raw_frames = ffprobe_frames.get("frames", [])
    units = _build_timed_units_from_frames(
        raw_frames,
        duration,
        fps,
    )

    segment_bits = _accumulate_bits_by_segment(units, duration, step)

    segments: List[Dict[str, Any]] = []
    for seg_idx, bits in enumerate(segment_bits):
        start = seg_idx * step
        end = min(start + step, duration)
        interval_seconds = max(0.0, end - start)

        bitrate_bps = bits / interval_seconds if interval_seconds > 0 else 0.0
        bitrate_norm = round(bitrate_bps / overall_bitrate, 3) if overall_bitrate > 0 else 0.0
        segments.append(
            {
                "segment": seg_idx + 1,
                "start(s)": round(start, 3),
                "end(s)": round(end, 3),
                "bitrate(bps)": int(round(bitrate_bps)),
                "bitrate(kbps)": f"{bitrate_bps / 1000.0:.3f}",
                "bitrate_norm": bitrate_norm,
            }
        )

    csv_path = output_dir / "bitrate_series.csv"
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "segment",
                "start(s)",
                "end(s)",
                "bitrate(bps)",
                "bitrate(kbps)",
                "bitrate_norm",
            ],
        )
        writer.writeheader()
        writer.writerows(segments)

    gop_rows = _build_gop_series(raw_frames, duration)
    gop_csv_path = output_dir / "gop_series.csv"
    with open(gop_csv_path, "w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "gop",
                "start(s)",
                "end(s)",
                "duration(s)",
                "frames",
                "keyframes",
                "i_frames",
                "p_frames",
                "b_frames",
                "bitrate(kbps)",
                "keyframe_interval(s)",
            ],
        )
        writer.writeheader()
        writer.writerows(gop_rows)

    return csv_path, gop_csv_path
