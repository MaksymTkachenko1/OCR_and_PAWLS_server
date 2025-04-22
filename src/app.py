from pathlib import Path
import os
from pawls_preprocess import preprocess, add_hash, assign
from tqdm import tqdm
import argparse
import pytesseract
from pdf2image import convert_from_path

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "results"

def process_file_plain_text(file_path):
    try:
        page_texts = []
        # pytesseract accept images as input.
        # You need to use pdf2image convert_from_path module to split the document image 
        # and sent the pages one by one to tesseract
        # append results of each page to page texts list
        # Convert PDF to a list of images
        images = convert_from_path(file_path)
        for i, image in enumerate(images):
            # Use pytesseract to extract text from each image (page)
            text = pytesseract.image_to_string(image)
            page_texts.append(text)
        
        # Save results to output folder
        result_file = Path(OUTPUT_DIR) / f"{file_path.stem}.txt"
        # Ensure output directory exists
        result_file.parent.mkdir(parents=True, exist_ok=True)
        with open(result_file, "w", encoding='utf-8') as f: # Added encoding='utf-8'
            f.write('\n\n'.join(page_texts)) # Corrected separator to \n\n

        print(f"Processed {file_path.name}")
    except Exception as e:
        print(f"Error processing {file_path.name}: {e}")

def main(args):
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if args.mode == "text":
        pdf_files = list(Path(INPUT_DIR).glob('*.pdf'))
        print(f"Found {len(pdf_files)} PDF files to process.")

        for file in tqdm(pdf_files, desc="Processing PDFs"):
            process_file_plain_text(file)
    elif args.mode=='pawls':
        add_hash(INPUT_DIR, OUTPUT_DIR)
        preprocess(OUTPUT_DIR / "skiff_files/apps/pawls/papers")
        assign(OUTPUT_DIR / "skiff_files/apps/pawls/papers")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Process PDF files.")
    parser.add_argument('--mode', type=str, help='Text extraction mode', choices=['text', 'pawls'])
    args = parser.parse_args()
    print(args)
    main(args)