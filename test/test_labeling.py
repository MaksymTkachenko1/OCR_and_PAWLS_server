import sys
sys.path.insert(0, "..")
import json
import os
from pathlib import Path

test_dir = Path(__file__).parent.parent.absolute()
results_dir = os.path.join(test_dir, 'results/labeled')

def test_folder_contains_results():
    all_files = os.listdir(results_dir)
    json_files = [f for f in all_files if f.endswith('.json')]
    assert json_files, "No PDF files found in the results directory."
    assert len(json_files) >= 5, "Not enough labeled documents in directory."

def test_json_files_have_required_labels():
    required_labels = ["Title", "Author", "Abstract", "Section", "Paragraph"]
    json_files = [f for f in os.listdir(results_dir) if f.endswith('.json')]
    for json_file in json_files:
        with open(os.path.join(results_dir, json_file), 'r') as file:
            data = json.load(file)
            labels = [item['label'].lower() for item in data]
            for label in required_labels:
                assert label.lower() in labels, f"{label} not found in {json_file}"

def test_tokens_have_required_fields():
    required_fields = ["text", "x0", "y0", "x1", "y1", "label", "box"]
    json_files = [f for f in os.listdir(results_dir) if f.endswith('.json')]
    for json_file in json_files:
        with open(os.path.join(results_dir, json_file), 'r') as file:
            data = json.load(file)
            for token in data:
                for field in required_fields:
                    assert field in token, f"Field '{field}' not found in token in {json_file}"