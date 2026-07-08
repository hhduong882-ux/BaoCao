from tkinter import filedialog, Tk
from pathlib import Path
from extract import extract_segment_bitrate
from metadata import extract_metadata
from visualize import plot_bitrate
import datetime
from zoneinfo import ZoneInfo

def select_video_file():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select a video file",
        filetypes=[("Video files", "*.mp4 *.avi *.mkv *.mov"), ("All files", "*.*")]
    )
    root.destroy()
    return file_path

def main():
    video_file = select_video_file()
    if not video_file:
        print("No video file selected")
        return
    video_path = Path(video_file)
    
    now_utc = datetime.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
    start_time = now_utc.strftime(format="%Y%m%d_%H%M%S")
    output_dir = Path(f"result/result_modun3/{start_time}({video_path.name})")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    extract_metadata(video_path=video_path, output_dir=output_dir)
    try:
        segment_duration = float(input("Enter segment_duration in seconds: "))
        if not isinstance(segment_duration, (int, float)) or segment_duration <= 0:
            raise ValueError("Gia tri segment_duration khong hop le !")
    except:
        print("Enter a number. Please")
        return
    
    
    bitrate_csv_path, gop_csv_path = extract_segment_bitrate(
        video_path=video_path,
        step=segment_duration,
        output_dir=output_dir,
    )

    try:
        downscale_factor = int(input("Enter downscale factor for plotting (e.g., 1 for no downscaling): "))
        if downscale_factor <= 0:
            raise ValueError
    except:
        print("Enter an integer > 0. Please")
        return

    plot_bitrate(csv_path=bitrate_csv_path, downscale_factor=downscale_factor, output_dir=output_dir)
    

if __name__ == "__main__":
    main()
    
  
  
