import json
import os
import getpass
from datasets import Dataset, DatasetDict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

CONFIG_FILE = os.path.join(PROJECT_ROOT, ".upload_config.json")

def main():
    print("Loading text data files...")
    train_file = os.path.join(DATA_DIR, "train.json")
    test_file = os.path.join(DATA_DIR, "test.json")
    
    if not os.path.exists(train_file) or not os.path.exists(test_file):
        print("Error: train.json or test.json not found in data/. Please run train_classifiers.py first.")
        return
        
    with open(train_file, "r", encoding="utf-8") as f:
        train_data = json.load(f)
    with open(test_file, "r", encoding="utf-8") as f:
        test_data = json.load(f)
            
    print(f"Loaded {len(train_data)} train and {len(test_data)} test records.")
    
    # Convert list of dicts to Hugging Face Dataset
    train_dataset = Dataset.from_list(train_data)
    test_dataset = Dataset.from_list(test_data)
    
    dataset_dict = DatasetDict({
        "train": train_dataset,
        "test": test_dataset
    })
    
    print("\nDataset ready with train/test splits!")
    print(dataset_dict)
    
    # Load or prompt for credentials
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
        repo_id = input("Enter your Hugging Face dataset repository name (e.g., katsufu/recruitment_data): ")
        
        # Save for next time
        if repo_id.strip() and token.strip():
            with open(CONFIG_FILE, "w") as f:
                json.dump({"token": token.strip(), "repo_id": repo_id.strip()}, f)
    
    if repo_id.strip() and token.strip():
        from huggingface_hub import HfApi
        api = HfApi()
        
        print(f"\nCreating repository '{repo_id}' if it doesn't exist...")
        try:
            api.create_repo(repo_id=repo_id, token=token.strip(), repo_type="dataset", exist_ok=True)
        except Exception as e:
            print(f"Notice from create_repo (you can usually ignore this): {e}")
            
        print(f"\nPushing to Hub at {repo_id}...")
        dataset_dict.push_to_hub(repo_id, token=token.strip())
        
        # Upload the Dataset Card if it exists
        dataset_readme = os.path.join(DATA_DIR, "dataset_README.md")
        if os.path.exists(dataset_readme):
            try:
                print("Uploading Dataset Card (README.md)...")
                api.upload_file(
                    path_or_fileobj=dataset_readme,
                    path_in_repo="README.md",
                    repo_id=repo_id,
                    repo_type="dataset",
                    token=token.strip()
                )
            except Exception as e:
                print(f"Notice: Could not upload dataset README: {e}")
                
        print(f"\nSuccess! Your dataset is now available at: https://huggingface.co/datasets/{repo_id}")
    else:
        print("Upload cancelled. Both token and repository name are required.")

if __name__ == "__main__":
    main()
