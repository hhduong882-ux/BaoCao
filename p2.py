import hashlib
import tkinter as tk
from tkinter import filedialog
import os
import json 

def calculate_sha256(file_path, chunk_size=65536):
    if not file_path:
        return None
        
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
    root = tk.Tk()
    root.attributes('-topmost', True)
    root.withdraw()
    
    file_path = filedialog.askopenfilename(
        title="Hãy chọn một video",
        filetypes=[
            ("Tệp Video", "*.mp4 *.avi *.mkv *.mov *.flv *.wmv"),
            ("Tất cả các tệp", "*.*")
        ]
    )
    
    root.destroy()
    return file_path

if __name__ == "__main__":
    tam = -1
    save_file = 'luutru.json' 
    
    while tam != 0:
        print('\n--- MENU QUẢN LÝ VIDEO ---')
        print('1. Lưu thông tin (Mã băm) vào file')
        print('2. Tiến hành kiểm tra với video trong kho')
        print('0. Thoát Chương Trình')
        print('--------------------------')
        
        try:
            tam = int(input("Sự lựa chọn của bạn: "))
        except ValueError:
            print("Lỗi: Vui lòng chỉ nhập số (0, 1 hoặc 2)!")
            continue

        if tam == 1:
            print("-> Chọn file mà bạn muốn lưu trữ...")
            video_path = choose_video_file()
            
            if video_path: 
                custom_name = input("Nhập tên gọi gợi nhớ cho video này: ").strip()
                if not custom_name:
                    custom_name = os.path.basename(video_path)
                
                print(f"Đang tính toán SHA-256...")
                hash_result1 = calculate_sha256(video_path)
                
                data = {
                    "ten_goi": custom_name,
                    "ma_bam": hash_result1
                }
                
                with open(save_file, 'a', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
                    file.write('\n')
                    
                print(f"✅ Đã lưu thành công với tên gọi: '{custom_name}'")
            else:
                print("❌ Thao tác bị hủy: Bạn chưa chọn video nào.")

        elif tam == 2:
            if not os.path.exists(save_file):
                print(f"❌ Lỗi: File '{save_file}' chưa tồn tại. Vui lòng chạy Lựa chọn 1 trước để lưu dữ liệu!")
                continue
            
            with open(save_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            if not data:
                print("❌ Kho dữ liệu hiện đang trống. Vui lòng thêm video mới!")
                continue

            print("-> Chọn file video bạn muốn kiểm tra...")
            video_path = choose_video_file()
            
            if video_path:
                print("\n--- DANH SÁCH VIDEO ĐÃ LƯU ---")
                for index, item in enumerate(data):
                    print(f"{index + 1}. [{item.get('ten_goi')}]")
                print("------------------------------")
                
                try:
                    chon_ten = int(input("Nhập số thứ tự của video bạn muốn đối chiếu: "))
                    # Lấy thông tin video đã chọn
                    selected_item = data[chon_ten - 1]
                    expected_hash = selected_item.get("ma_bam")
                    expected_name = selected_item.get("ten_goi")
                        
                    print(f"\nĐang tính toán SHA-256 cho file vừa chọn: {os.path.basename(video_path)}...")
                    new_hash = calculate_sha256(video_path)
                        
                    print(f"\nĐang so sánh với hồ sơ: [{expected_name}]...")
                    if new_hash == expected_hash:
                        print("✅ Kết quả: GIỐNG NHAU (Đây chính xác là video bạn đã lưu, dữ liệu nguyên vẹn)")
                    else:
                        print("⚠️ Kết quả: KHÁC NHAU (Đây không phải là video đó, hoặc video đã bị chỉnh sửa/hỏng)")
                except ValueError:
                    print("❌ Lỗi: Vui lòng nhập một số hợp lệ.")
            else:
                print("❌ Thao tác bị hủy: Bạn chưa chọn video nào.")
                
        elif tam == 0:
            print("Đang thoát chương trình. Tạm biệt!")
        else:
            print("Lựa chọn không hợp lệ, vui lòng chọn lại.")