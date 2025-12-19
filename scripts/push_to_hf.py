import os
from dotenv import load_dotenv
from huggingface_hub import HfApi, login

# Load environment variables
load_dotenv()

# Get HF token
hf_token = os.getenv("HF_TOKEN")
if not hf_token:
    raise ValueError("HF_TOKEN not found in .env file")

# Login to Hugging Face
login(token=hf_token)

# Initialize the API
api = HfApi()

# Define paths and repo
checkpoint_folder = "checkpoints/1.5Bv2/step_0007000"
repo_id = "JayLL13/VoxCPM-1.5B-VN"

# Files to upload (excluding optimizer.pth as it's only needed for training)
files_to_upload = [
    "audiovae.pth",
    "config.json",
    "model.safetensors",
    "scheduler.pth",
    "special_tokens_map.json",
    "tokenizer.json",
    "tokenizer_config.json",
]

print(f"Pushing model to {repo_id}...")

# Create repo if it doesn't exist
try:
    api.create_repo(repo_id=repo_id, exist_ok=True, private=False)
    print(f"Repository {repo_id} is ready")
except Exception as e:
    print(f"Note: {e}")

# Upload each file
for filename in files_to_upload:
    local_path = os.path.join(checkpoint_folder, filename)
    if os.path.exists(local_path):
        print(f"Uploading {filename}...")
        api.upload_file(
            path_or_fileobj=local_path,
            path_in_repo=filename,
            repo_id=repo_id,
        )
        print(f"  ✓ {filename} uploaded successfully")
    else:
        print(f"  ✗ {filename} not found, skipping")

print(f"\nDone! Model pushed to https://huggingface.co/{repo_id}")
