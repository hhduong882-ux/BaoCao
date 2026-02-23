import hashlib
import tkinter as tk
from tkinter import filedialog

def calculate_sha256(file_path, chunk_size=65536):
    
    sha256_hash = hashlib.sha256()
    
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(chunk_size), b""):
                sha256_hash.update(byte_block)
                
        return sha256_hash.hexdigest()
        
    except FileNotFoundError:
        return "Lỗi: Không tìm thấy tệp video."
    except Exception as e:
        return f"Đã xảy ra lỗi: {e}"
def choose_video_file():
    # 1. Khởi tạo một cửa sổ gốc (root window) của tkinter
    root = tk.Tk()
    root.attributes('-topmost', True)
    # 2. Ẩn cửa sổ gốc đi, vì chúng ta chỉ muốn hiện hộp thoại chọn file
    root.withdraw()
    
    # 3. Mở hộp thoại và thiết lập bộ lọc chỉ hiển thị các tệp video
    file_path = filedialog.askopenfilename(
        title="Hãy chọn một video để xử lý",
        filetypes=[
            ("Tệp Video", "*.mp4 *.avi *.mkv *.mov *.flv *.wmv"),
            ("Tất cả các tệp", "*.*")
        ]
    )
    
    return file_path
# --- Ví dụ cách sử dụng ---
if __name__ == "__main__":
    # Thay đường dẫn này bằng đường dẫn video thực tế của bạn
    tam = -1
    while tam != 0 :
        print('1. Lưu thông tin vào file')
        print('2. Tiến hành kiểm tra với video trong kho')
        print('0. Thoát Chương Trình')
        tam = int(input("Sự lựa chọn của bạn: "))
        if tam == 1:
            print("Chọn file mà bạn muốn lưu trữ")
            video_path = choose_video_file()
            print(f"Đang tính toán SHA-256 ")
            hash_result1 = calculate_sha256(video_path)
            save = 'luutru.txt'
            with open(save, 'w', encoding='utf-8') as file:
                file.write(hash_result1)
            print("ghi thành công")
        if tam == 2:
            file_path = "luutru.txt"
            video_path = choose_video_file()
            print(f"Đang tính toán SHA-256 ")
            hash_result2 = calculate_sha256(video_path)
            with open(file_path, 'r', encoding='utf-8') as file:
                temp = file.read()
            if hash_result2 == temp:
                print("Kết quả: GIỐNG NHAU (Dữ liệu không bị thay đổi)")
            else:
                print("Kết quả: KHÁC NHAU (Dữ liệu đã bị chỉnh sửa)")


    
            

        
    
    