import csv
from pathlib import Path
import statistics
import matplotlib.pyplot as plt
import numpy as np


def load_bitrate_csv(csv_path: Path):
   
    segments = []
    times = []
    bitrate_norm = []
    bitrate_kbps = []

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            segments.append(int(row["segment"]))
            times.append(float(row["start(s)"]))
            bitrate_norm.append(float(row["bitrate_norm"]))
            bitrate_kbps.append(float(row["bitrate(kbps)"]))

    return segments, times, bitrate_norm, bitrate_kbps


def downscale_series(x, y, factor: int, agg: str = "max"):
    
    if factor <= 1:
        return x, y

    ds_x, ds_y = [], []

    for i in range(0, len(y), factor):
        chunk_y = y[i:i + factor]
        chunk_x = x[i:i + factor]

        if not chunk_y:
            continue

        ds_x.append(chunk_x[0])
        if agg == "mean":
            ds_y.append(float(sum(chunk_y) / len(chunk_y)))
        else:
            ds_y.append(max(chunk_y))

    return ds_x, ds_y


def _set_time_xticks(x_values):
    if not x_values:
        return

    max_time = max(x_values)
    if max_time <= 0:
        return

    target_ticks = 12
    step = max(1, int(np.ceil(max_time / target_ticks)))
    xticks = np.arange(0, max_time + step, step)
    plt.xticks(xticks)


def plot_bitrate(
    csv_path: Path,
    downscale_factor: int,
    output_dir: Path
):
    output_dir.mkdir(parents=True, exist_ok=True)
    output_img = output_dir / "bitrate_plot.png"

    _segments, times, bitrate_norm, _ = load_bitrate_csv(csv_path)

    mean_value = statistics.mean(bitrate_norm)

    plot_x, plot_y = downscale_series(
        times, bitrate_norm, downscale_factor
    )


    if len(plot_x) > 1:
        bar_width = plot_x[1] - plot_x[0]
    else:
        bar_width = 0.8

    plt.figure(figsize=(12, 5))
    plt.bar(
        plot_x,
        plot_y,
        width=bar_width,
        align="edge"
    )
    

    _set_time_xticks(plot_x)

    # Mean line
    plt.axhline(
        y=mean_value,
        linestyle="--",
        linewidth=1,
        label=f"Mean = {mean_value:.2f}"
    )

    plt.xlabel("Time (seconds)")
    plt.ylabel("Normalized bitrate")
    plt.title("Bitrate per segment (normalized)")
    plt.legend()
    plt.grid(True, axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_img, dpi=150)
    plt.close()

    return output_img
