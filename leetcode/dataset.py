import json
import re
from typing import Dict, List, Optional
import os
import pandas as pd
import yaml
from datasets import Dataset, DatasetDict, load_dataset
from dotenv import dotenv_values
from huggingface_hub import HfApi, create_repo


def load_jsonl(file_path):
    data = []
    with open(file_path, "r") as file:
        for line in file:
            try:
                json_obj = json.loads(line.strip())
                data.append(json_obj)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON on line: {line}")
                print(f"Error message: {str(e)}")
    return data


def extract_and_remove_followup(content):
    match = re.search(r"\*\*Follow-up:\*\*(.*?)$", content, re.DOTALL)
    if match:
        followup = match.group(1).strip()
        content_without_followup = content[: match.start()].strip()
        return content_without_followup, followup
    return content, None


def process_data(data):
    processed_data = []
    for item in data:
        content, followup = extract_and_remove_followup(item["content"])
        processed_item = {
            "id": item["id"],
            "title": item["title"],
            "content": content,
            "followup": followup,
            "python_code": item["code"].get("python", "") if "code" in item else "",
        }
        processed_data.append(processed_item)
    return processed_data


def create_dataframe(data):
    return pd.DataFrame(data)


def create_dataset_dict(data):
    dataset = Dataset.from_pandas(pd.DataFrame(data))
    return DatasetDict({"train": dataset})


def create_dataset_card(dataset: DatasetDict, dataset_name: str) -> str:
    def get_features(ds: Dataset) -> List[Dict[str, str]]:
        return [
            {"name": name, "dtype": str(feature.dtype)}
            for name, feature in ds.features.items()
        ]

    def get_size_category(total_examples: int) -> str:
        categories = [
            ("n<1K", 1000),
            ("1K<n<10K", 10000),
            ("10K<n<100K", 100000),
            ("100K<n<1M", 1000000),
        ]
        for category, threshold in categories:
            if total_examples < threshold:
                return category
        return "1M<n<10M"

    total_examples = sum(len(ds) for ds in dataset.values())
    metadata = {
        "license": "apache-2.0",
        "language": ["en"],
        "pretty_name": dataset_name,
        "size_categories": [get_size_category(total_examples)],
        "tags": ["code", "leetcode"],
        "dataset_info": {
            "features": get_features(next(iter(dataset.values()))),
            "splits": [
                {"name": split, "num_examples": len(ds)}
                for split, ds in dataset.items()
            ],
        },
    }
    return f"---\n{yaml.dump(metadata, sort_keys=False)}---\n"


def push_to_hub(
    dataset: DatasetDict, repo_name: str, card_content: str, token: str
) -> None:
    temp_readme = f"temp_README_{repo_name.split('/')[-1]}.md"
    with open(temp_readme, "w") as f:
        f.write(card_content)

    try:
        create_repo(repo_name, token=token, repo_type="dataset", exist_ok=True)
    except Exception as e:
        print(f"Error creating repository: {e}")
        return

    dataset.push_to_hub(repo_name, token=token)

    api = HfApi()
    api.upload_file(
        path_or_fileobj=temp_readme,
        path_in_repo="README.md",
        repo_id=repo_name,
        repo_type="dataset",
        token=token,
    )

    os.remove(temp_readme)


if __name__ == "__main__":
    # Usage
    file_path = "leetcode/leetcode-rosetta.jsonl"  # Replace with your actual file path
    loaded_data = load_jsonl(file_path)
    processed_data = process_data(loaded_data)

    # Create DataFrame
    df = create_dataframe(processed_data)
    print("DataFrame created. Shape:", df.shape)
    print("\nFirst few rows of the DataFrame:")
    print(df.head())

    # Create DatasetDict
    dataset_dict = create_dataset_dict(processed_data)
    print("\nDatasetDict created. Keys:", dataset_dict.keys())
    print(f"Number of items in 'train' split: {len(dataset_dict['train'])}")

    # Example of how to use the DatasetDict with Hugging Face
    print("\nTo upload to Hugging Face Hub, you can use:")
    print("dataset_dict.push_to_hub('your-username/your-dataset-name')")

    # If you want to save locally first:
    print("\nTo save locally:")
    print("dataset_dict.save_to_disk('path/to/local/directory')")

    # To load a saved dataset:
    print("\nTo load a saved dataset:")
    print("from datasets import load_from_disk")
    print("loaded_dataset = load_from_disk('path/to/local/directory')")

    dataset_card = create_dataset_card(dataset_dict, "leetcode-rosetta")

    HF_TOKEN = dotenv_values(".env")["HF_WRITE_TOKEN"]
    push_to_hub(dataset_dict, "scottsuk0306/leetcode-rosetta", dataset_card, HF_TOKEN)
    print("Datasets have been pushed to the Hugging Face Hub!")
