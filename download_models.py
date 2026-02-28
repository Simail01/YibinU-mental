
import os
import sys

# Try to import huggingface_hub
try:
    from huggingface_hub import snapshot_download
except ImportError:
    print("Please install huggingface_hub first: pip install huggingface_hub")
    sys.exit(1)

# Define project root and model directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
MODEL_BASE_DIR = os.path.join(PROJECT_ROOT, "model")

# Create model directory if not exists
os.makedirs(MODEL_BASE_DIR, exist_ok=True)

# Define models to download (repo_id -> local_folder_name)
MODELS = {
    "zwzzz/Chinese-MentalBERT": "Chinese-MentalBERT",
    "THUDM/chatglm2-6b-int4": "Chatglm2-6b-int4",
    "shibing624/text2vec-base-chinese": "text2vec-base-chinese"
}

def download_models():
    print(f"Models will be downloaded to: {MODEL_BASE_DIR}")
    print("Starting download process...")
    print("Note: This may take a while depending on your network speed.")
    
    for repo_id, folder_name in MODELS.items():
        local_dir = os.path.join(MODEL_BASE_DIR, folder_name)
        print(f"\n--------------------------------------------------")
        print(f"Downloading {repo_id} to {local_dir}...")
        
        try:
            snapshot_download(
                repo_id=repo_id,
                local_dir=local_dir,
                local_dir_use_symlinks=False, # Ensure actual files are downloaded for offline use
                resume_download=True
            )
            print(f"✅ Successfully downloaded {repo_id}")
        except Exception as e:
            print(f"❌ Failed to download {repo_id}: {e}")
            print("Please check your network connection or try using a mirror site.")
            # Suggest setting HF_ENDPOINT for Chinese users
            print("Tip: If you are in China, try setting environment variable: HF_ENDPOINT=https://hf-mirror.com")

    print("\n--------------------------------------------------")
    print("All download tasks completed.")
    print(f"Please check the directory: {MODEL_BASE_DIR}")

if __name__ == "__main__":
    download_models()
