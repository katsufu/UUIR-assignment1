import os
import getpass
import json
from huggingface_hub import HfApi

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
MODEL_FOLDER = os.path.join(PROJECT_ROOT, "trained_model")
CONFIG_FILE = os.path.join(PROJECT_ROOT, ".upload_model_config.json")

def main():
    if not os.path.exists(MODEL_FOLDER):
        print(f"Error: {MODEL_FOLDER} does not exist. Please train the model first.")
        return
        
    print("Preparing to upload model to Hugging Face Model Hub...")
    
    token = ""
    repo_id = ""
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                token = config.get("token", "")
                repo_id = config.get("repo_id", "")
        except Exception:
            pass
            
    if repo_id and token:
        use_saved = input(f"\nFound saved configuration for repository '{repo_id}'. Use this? (y/n): ")
        if use_saved.lower() != 'y':
            repo_id = ""
            token = ""
            
    if not repo_id or not token:
        print("\nTo upload to Hugging Face, you will need an Access Token with 'write' permissions.")
        print("You can get one from: https://huggingface.co/settings/tokens")
        
        token = getpass.getpass("\nEnter your Hugging Face Access Token (input will be hidden): ")
        repo_id = input("Enter your Hugging Face model repository name (e.g., your_username/article_classifier): ")
        
        if repo_id.strip() and token.strip():
            with open(CONFIG_FILE, "w") as f:
                json.dump({"token": token.strip(), "repo_id": repo_id.strip()}, f)
                
    if repo_id.strip() and token.strip():
        api = HfApi()
        
        print(f"\nCreating repository '{repo_id}' if it doesn't exist...")
        try:
            api.create_repo(repo_id=repo_id, token=token.strip(), repo_type="model", exist_ok=True)
        except Exception as e:
            # Usually raises an error if it already exists, which is fine
            pass
            
        print(f"Uploading files from {MODEL_FOLDER} to https://huggingface.co/{repo_id}...")
        try:
            api.upload_folder(
                folder_path=MODEL_FOLDER,
                repo_id=repo_id,
                repo_type="model",
                token=token.strip()
            )
            print(f"\nSuccess! Your model is now available at: https://huggingface.co/{repo_id}")
        except Exception as e:
            print(f"Error uploading model: {e}")
    else:
        print("Upload cancelled. Both token and repository name are required.")

if __name__ == "__main__":
    main()
