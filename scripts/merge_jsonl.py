"""
Script để tổng hợp 2 file JSONL thành 1 file.
Audio paths sẽ được chuyển thành absolute path.

Usage:
    python merge_jsonl.py <jsonl_file_1> <jsonl_file_2> <output_jsonl>

Example:
    python merge_jsonl.py /mnt/d/tts_dataset/metadata.jsonl /mnt/c/Users/xuhet/Downloads/tts_dataset/metadata.jsonl /mnt/d/merged_metadata.jsonl
"""

import os
import json
import argparse


def merge_jsonl_files(jsonl_path_1: str, jsonl_path_2: str, output_path: str):
    """
    Tổng hợp 2 file JSONL thành 1 file.
    Chuyển đổi audio path thành absolute path.
    
    Args:
        jsonl_path_1: Đường dẫn đến file JSONL thứ nhất
        jsonl_path_2: Đường dẫn đến file JSONL thứ hai
        output_path: Đường dẫn file JSONL output
    """
    total_entries = 0
    
    # Tạo thư mục output nếu chưa tồn tại
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as out_file:
        # Xử lý file JSONL thứ nhất
        print(f"📖 Đang đọc: {jsonl_path_1}")
        with open(jsonl_path_1, "r", encoding="utf-8") as f1:
            for line in f1:
                line = line.strip()
                if not line:
                    continue
                    
                entry = json.loads(line)
                
                # Chuyển audio path thành absolute path
                if "audio" in entry:
                    entry["audio"] = os.path.abspath(entry["audio"])
                
                out_file.write(json.dumps(entry, ensure_ascii=False) + "\n")
                total_entries += 1
        
        print(f"✅ Đã xử lý {total_entries} entries từ file 1")
        count_file_1 = total_entries
        
        # Xử lý file JSONL thứ hai
        print(f"📖 Đang đọc: {jsonl_path_2}")
        with open(jsonl_path_2, "r", encoding="utf-8") as f2:
            for line in f2:
                line = line.strip()
                if not line:
                    continue
                    
                entry = json.loads(line)
                
                # Chuyển audio path thành absolute path
                if "audio" in entry:
                    entry["audio"] = os.path.abspath(entry["audio"])
                
                out_file.write(json.dumps(entry, ensure_ascii=False) + "\n")
                total_entries += 1
        
        count_file_2 = total_entries - count_file_1
        print(f"✅ Đã xử lý {count_file_2} entries từ file 2")
    
    print(f"\n🎉 DONE! Tổng hợp thành công:")
    print(f"   - File 1: {count_file_1} entries")
    print(f"   - File 2: {count_file_2} entries")
    print(f"   - Tổng cộng: {total_entries} entries")
    print(f"   - Output: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Tổng hợp 2 file JSONL thành 1 file với absolute audio paths"
    )
    parser.add_argument(
        "jsonl_file_1",
        type=str,
        help="Đường dẫn đến file JSONL thứ nhất"
    )
    parser.add_argument(
        "jsonl_file_2",
        type=str,
        help="Đường dẫn đến file JSONL thứ hai"
    )
    parser.add_argument(
        "output_jsonl",
        type=str,
        help="Đường dẫn file JSONL output"
    )
    
    args = parser.parse_args()
    
    # Kiểm tra file tồn tại
    if not os.path.exists(args.jsonl_file_1):
        print(f"❌ Lỗi: File không tồn tại: {args.jsonl_file_1}")
        return
    
    if not os.path.exists(args.jsonl_file_2):
        print(f"❌ Lỗi: File không tồn tại: {args.jsonl_file_2}")
        return
    
    merge_jsonl_files(args.jsonl_file_1, args.jsonl_file_2, args.output_jsonl)


if __name__ == "__main__":
    main()
