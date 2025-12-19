import os
import csv
import json
import shutil
from datasets import load_dataset, Audio
from tqdm import tqdm
import soundfile as sf
import librosa
from dotenv import load_dotenv
load_dotenv()
TARGET_SR = 44100  # Target sample rate

# ========== CONFIG ==========
HF_TOKEN = os.getenv("HF_TOKEN")
HF_DATASET = "dolly-vn/dolly-audio-1000h-vietnamese"     # ví dụ: "librispeech_asr"
HF_SPLIT = "train"                       # train / validation / test
PARENT_DIR = "/mnt/d/tts_dataset/"                   # folder output
PARENT_DIR_BACKUP = "/mnt/c/Users/xuhet/Downloads/tts_dataset/"            # folder backup khi hết dung lượng

AUDIO_COLUMN = "audio"                   # cột audio trong HF dataset
TEXT_COLUMN = "text"                     # cột transcript
MIN_FREE_SPACE_GB = 0.3                  # Ngưỡng dung lượng trống tối thiểu (GB)
# ============================


def get_free_space_gb(path):
    """Trả về dung lượng trống của ổ đĩa chứa path (tính bằng GB)."""
    total, used, free = shutil.disk_usage(path)
    return free / (1024 ** 3)


def main():
    # Biến để theo dõi thư mục đang dùng
    current_parent_dir = PARENT_DIR
    switched_to_backup = False

    # Tạo thư mục output
    wavs_dir = os.path.join(current_parent_dir, "wavs")
    os.makedirs(wavs_dir, exist_ok=True)

    metadata_path = os.path.join(current_parent_dir, "metadata.csv")
    jsonl_path = os.path.join(current_parent_dir, "metadata.jsonl")
    
    csv_file = open(metadata_path, "w", newline="", encoding="utf-8")
    jsonl_file = open(jsonl_path, "w", encoding="utf-8")
    writer = csv.writer(csv_file, delimiter="|")

    print(f"📥 Loading dataset {HF_DATASET} (streaming)...")

    # 🔥 FIX QUAN TRỌNG: ép audio decode sang numpy
    dataset = load_dataset(
        HF_DATASET,
        split=HF_SPLIT,
        streaming=True,
        token=HF_TOKEN
    ).cast_column(AUDIO_COLUMN, Audio(decode=True))

    print("🎧 Bắt đầu tải và lưu audio...")

    idx = 1
    for sample in tqdm(dataset, desc="Processing"):
        audio_obj = sample[AUDIO_COLUMN]

        # HF trả về:
        # audio_obj["array"]  (numpy array)
        # audio_obj["sampling_rate"]

        array = audio_obj["array"]
        sr = audio_obj["sampling_rate"]

        # Resample to target sample rate (44.1kHz)
        if sr != TARGET_SR:
            array = librosa.resample(array, orig_sr=sr, target_sr=TARGET_SR)
            sr = TARGET_SR

        # Tên file output
        filename = f"audio_{idx:06d}.wav"
        filepath = os.path.join(wavs_dir, filename)

        # Save bằng soundfile
        sf.write(filepath, array, sr)

        # Transcript
        text = sample[TEXT_COLUMN].replace("\n", " ").strip()

        # Calculate duration in seconds
        duration = round(len(array) / sr, 2)

        # Ghi metadata CSV
        writer.writerow([filename, text])

        # Ghi metadata JSONL
        jsonl_entry = {
            "audio": os.path.join(current_parent_dir, "wavs", filename),
            "text": text,
            "duration": duration
        }
        jsonl_file.write(json.dumps(jsonl_entry, ensure_ascii=False) + "\n")

        # Kiểm tra dung lượng đĩa sau mỗi iteration
        if not switched_to_backup:
            free_space = get_free_space_gb(current_parent_dir)
            if free_space < MIN_FREE_SPACE_GB:
                print(f"\n⚠️ Ổ đĩa hiện tại còn {free_space:.2f} GB (< {MIN_FREE_SPACE_GB} GB)")
                print(f"🔄 Chuyển sang thư mục backup: {PARENT_DIR_BACKUP}")
                
                # Đóng các file metadata hiện tại
                csv_file.close()
                jsonl_file.close()
                
                # Chuyển sang thư mục backup
                current_parent_dir = PARENT_DIR_BACKUP
                switched_to_backup = True
                
                # Tạo thư mục backup
                wavs_dir = os.path.join(current_parent_dir, "wavs")
                os.makedirs(wavs_dir, exist_ok=True)
                
                # Mở file metadata mới ở thư mục backup (append mode)
                metadata_path = os.path.join(current_parent_dir, "metadata.csv")
                jsonl_path = os.path.join(current_parent_dir, "metadata.jsonl")
                csv_file = open(metadata_path, "a", newline="", encoding="utf-8")
                jsonl_file = open(jsonl_path, "a", encoding="utf-8")
                writer = csv.writer(csv_file, delimiter="|")
                
                print(f"✅ Đã chuyển sang {PARENT_DIR_BACKUP}, tiếp tục xử lý...")

        idx += 1

    csv_file.close()
    jsonl_file.close()
    print("✅ DONE! Saved to:", current_parent_dir)
    if switched_to_backup:
        print(f"📁 Dữ liệu được chia thành 2 ổ đĩa: {PARENT_DIR} và {PARENT_DIR_BACKUP}")


if __name__ == "__main__":
    main()