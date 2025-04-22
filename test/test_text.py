import sys
sys.path.insert(0, "..")
import os
from pathlib import Path

test_dir = Path(__file__).parent.parent.absolute()
uploads_dir = os.path.join(test_dir, 'uploads')
results_dir = os.path.join(test_dir, 'results')

def test_pdf_correspondence():
    pdf_files = [f for f in os.listdir(uploads_dir) if f.endswith('.pdf')]
    assert pdf_files, "No PDF files found in the uploads directory."
    for pdf_file in pdf_files:
        base_name = os.path.splitext(pdf_file)[0]
        txt_file = base_name + '.txt'
        txt_file_path = os.path.join(results_dir, txt_file)
        assert os.path.exists(txt_file_path), f"{txt_file} does not exist"

def test_uploads_folder_contains_pdf():
    all_files = os.listdir(uploads_dir)
    pdf_files = [f for f in all_files if f.endswith('.pdf')]
    assert pdf_files, "No PDF files found in the uploads directory."

def test_txt_files_have_content():
    txt_files = [f for f in os.listdir(results_dir) if f.endswith('.txt')]
    for txt_file in txt_files:
        file_path = os.path.join(results_dir, txt_file)
        assert os.path.getsize(file_path) > 0, f"{txt_file} is empty"