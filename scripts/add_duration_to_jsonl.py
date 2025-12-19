#!/usr/bin/env python3
"""
Script to add duration column to JSONL manifest file.
This speeds up training by avoiding audio decoding during compute_sample_lengths.

Usage:
    python scripts/add_duration_to_jsonl.py <input_jsonl> <output_jsonl>

Example:
    python scripts/add_duration_to_jsonl.py /mnt/d/tts_dataset/merged_metadata.jsonl /mnt/d/tts_dataset/merged_metadata_with_duration.jsonl
"""

import json
import sys
import os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

try:
    import soundfile as sf
except ImportError:
    print("Error: soundfile is required. Install with: pip install soundfile")
    sys.exit(1)

from tqdm import tqdm


def get_audio_duration(audio_path: str) -> float:
    """Get audio duration in seconds using soundfile (fast, doesn't decode full audio)."""
    try:
        info = sf.info(audio_path)
        return info.duration
    except Exception as e:
        print(f"Warning: Could not read {audio_path}: {e}")
        return -1.0


def process_line(line: str, audio_key: str = "wav") -> str:
    """Process a single JSONL line and add duration."""
    try:
        data = json.loads(line.strip())
        
        # Skip if duration already exists
        if "duration" in data and data["duration"] is not None and data["duration"] > 0:
            return json.dumps(data, ensure_ascii=False)
        
        # Get audio path - try common keys
        audio_path = None
        for key in [audio_key, "audio", "wav", "path", "audio_path", "file"]:
            if key in data:
                audio_path = data[key]
                if isinstance(audio_path, dict) and "path" in audio_path:
                    audio_path = audio_path["path"]
                break
        
        if audio_path and os.path.exists(audio_path):
            duration = get_audio_duration(audio_path)
            data["duration"] = duration
        else:
            print(f"Warning: Audio path not found or doesn't exist: {audio_path}")
            data["duration"] = -1.0
        
        return json.dumps(data, ensure_ascii=False)
    except json.JSONDecodeError as e:
        print(f"Warning: Could not parse JSON line: {e}")
        return line.strip()


def main():
    if len(sys.argv) < 3:
        print("Usage: python add_duration_to_jsonl.py <input_jsonl> <output_jsonl> [audio_key]")
        print("\nArguments:")
        print("  input_jsonl  : Path to input JSONL file")
        print("  output_jsonl : Path to output JSONL file with duration added")
        print("  audio_key    : Optional. Key for audio path in JSON (default: 'wav')")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    audio_key = sys.argv[3] if len(sys.argv) > 3 else "wav"
    
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    # Count total lines for progress bar
    print("Counting lines...")
    with open(input_path, "r", encoding="utf-8") as f:
        total_lines = sum(1 for _ in f)
    print(f"Total samples: {total_lines}")
    
    # Process with multiprocessing for speed
    num_workers = min(multiprocessing.cpu_count(), 16)
    print(f"Processing with {num_workers} workers...")
    
    # Read all lines
    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Process lines with progress bar
    results = []
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(process_line, line, audio_key): i for i, line in enumerate(lines)}
        
        with tqdm(total=total_lines, desc="Adding duration", unit="samples") as pbar:
            for future in as_completed(futures):
                results.append((futures[future], future.result()))
                pbar.update(1)
    
    # Sort by original order
    results.sort(key=lambda x: x[0])
    
    # Write output
    print(f"\nWriting output to {output_path}...")
    with open(output_path, "w", encoding="utf-8") as f:
        for _, line in results:
            f.write(line + "\n")
    
    print(f"Done! Output written to {output_path}")
    print(f"\nNow update your config to use: {output_path}")


if __name__ == "__main__":
    main()
