from huggingface_hub import snapshot_download
snapshot_download("openbmb/VoxCPM1.5", local_dir="./pretrained/VoxCPM-1.5B")
snapshot_download("openbmb/VoxCPM-0.5B", local_dir="./pretrained/VoxCPM-0.5B")