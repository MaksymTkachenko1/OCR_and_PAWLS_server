import json
from pathlib import Path
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration ---
# Use relative paths to ensure portability, assuming the script is run from the project root (Module_1_Intro)
# Adjust these if your script execution context is different.
# PAWLS_PAPERS_DIR is typically where PAWLS saves its output for each paper.
PAWLS_PAPERS_DIR = Path("pawls/skiff_files/apps/pawls/papers")
# OUTPUT_DIR is where the final DocBank JSON files will be saved.
OUTPUT_DIR = Path("results/labeled")
# --- End Configuration ---

def load_json(file_path: Path):
    """Loads a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from file: {file_path}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred loading {file_path}: {e}")
        return None

def find_annotation_file(paper_dir: Path) -> Path | None:
    """Finds the annotation file (ending with _annotations.json) in a directory."""
    try:
        annotation_files = list(paper_dir.glob('*_annotations.json'))
        if not annotation_files:
            logging.warning(f"No annotation file found in {paper_dir}")
            return None
        if len(annotation_files) > 1:
            logging.warning(f"Multiple annotation files found in {paper_dir}, using the first one: {annotation_files[0]}")
        return annotation_files[0]
    except Exception as e:
        logging.error(f"Error finding annotation file in {paper_dir}: {e}")
        return None

def process_paper(paper_id: str, pawls_base_dir: Path, output_base_dir: Path):
    """Processes a single paper's PAWLS output and converts it to DocBank format."""
    logging.info(f"Processing paper: {paper_id}")
    paper_dir = pawls_base_dir / paper_id
    pdf_structure_path = paper_dir / "pdf_structure.json"
    annotation_path = find_annotation_file(paper_dir)

    if not pdf_structure_path.exists():
        logging.error(f"pdf_structure.json not found for paper {paper_id} in {paper_dir}. Skipping.")
        return
    if not annotation_path:
        logging.error(f"Annotation file not found for paper {paper_id} in {paper_dir}. Skipping.")
        return

    # Load the data
    pdf_structure = load_json(pdf_structure_path)
    annotations_data = load_json(annotation_path)

    if pdf_structure is None or annotations_data is None:
        logging.error(f"Failed to load required JSON files for paper {paper_id}. Skipping.")
        return

    # --- Prepare pdf_structure tokens for efficient lookup ---
    # Create a dictionary where keys are (page_index, token_index) and values are the token objects.
    # This is generally more robust than assuming lists map directly if structures vary.
    tokens_map = {}
    for page_data in pdf_structure:
        page_index = page_data.get("page", {}).get("index")
        if page_index is None:
            logging.warning(f"Page index missing in pdf_structure for paper {paper_id}. Skipping page.")
            continue
        for token_index, token in enumerate(page_data.get("tokens", [])):
            tokens_map[(page_index, token_index)] = token
    # --- End Token Preparation ---

    docbank_output = []

    # --- Iterate through annotations and create DocBank entries ---
    for annotation in annotations_data.get("annotations", []):
        label_info = annotation.get("label")
        if not label_info or "text" not in label_info:
            logging.warning(f"Annotation missing label text for paper {paper_id}. Skipping annotation.")
            continue
        label_text = label_info["text"]

        for token_ref in annotation.get("tokens", []):
            page_index = token_ref.get("pageIndex")
            token_index = token_ref.get("tokenIndex")

            if page_index is None or token_index is None:
                logging.warning(f"Token reference missing pageIndex or tokenIndex in {annotation_path}. Skipping token reference.")
                continue

            # Find the corresponding token in the pdf_structure map
            pdf_token = tokens_map.get((page_index, token_index))

            if pdf_token is None:
                logging.warning(f"Token ({page_index}, {token_index}) referenced in {annotation_path} not found in {pdf_structure_path}. Skipping.")
                continue

            # Extract data and perform calculations
            try:
                x0 = float(pdf_token["x"])
                y0 = float(pdf_token["y"])
                width = float(pdf_token["width"])
                height = float(pdf_token["height"])
                text = pdf_token["text"]

                x1 = x0 + width
                y1 = y0 + height

                docbank_token = {
                    "text": text,
                    "x0": round(x0, 2), # Rounding for cleaner output, adjust as needed
                    "y0": round(y0, 2),
                    "x1": round(x1, 2),
                    "y1": round(y1, 2),
                    # "r": 0, # Skipping as requested
                    # "g": 0, # Skipping as requested
                    # "b": 0, # Skipping as requested
                    # "font_name": "...", # Skipping as requested
                    "label": label_text,
                    "box": [round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)]
                }
                docbank_output.append(docbank_token)
            except KeyError as e:
                logging.warning(f"Token ({page_index}, {token_index}) missing expected key {e} in {pdf_structure_path}. Skipping.")
            except (ValueError, TypeError) as e:
                 logging.warning(f"Error processing token ({page_index}, {token_index}) data ({pdf_token}): {e}. Skipping.")
    # --- End Annotation Iteration ---


    # --- Save the results ---
    output_file = output_base_dir / f"{paper_id}.json"
    try:
        # Ensure output directory exists
        output_base_dir.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(docbank_output, f, indent=4) # Use indent for readability
        logging.info(f"Successfully converted annotations for {paper_id} to {output_file}")
    except Exception as e:
        logging.error(f"Failed to save DocBank JSON for {paper_id} to {output_file}: {e}")
    # --- End Saving ---

def main():
    """Main function to orchestrate the conversion process."""
    logging.info("Starting PAWLS to DocBank conversion script.")
    logging.info(f"Looking for paper data in: {PAWLS_PAPERS_DIR.resolve()}")
    logging.info(f"Outputting DocBank files to: {OUTPUT_DIR.resolve()}")

    if not PAWLS_PAPERS_DIR.is_dir():
        logging.error(f"Input directory not found: {PAWLS_PAPERS_DIR}")
        print(f"Error: Input directory {PAWLS_PAPERS_DIR} not found. Please ensure PAWLS output exists.")
        return

    # Create the output directory if it doesn't exist
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logging.error(f"Could not create output directory {OUTPUT_DIR}: {e}")
        print(f"Error: Could not create output directory {OUTPUT_DIR}. Check permissions.")
        return

    paper_ids = [d.name for d in PAWLS_PAPERS_DIR.iterdir() if d.is_dir()]

    if not paper_ids:
        logging.warning(f"No paper subdirectories found in {PAWLS_PAPERS_DIR}.")
        print(f"Warning: No paper subdirectories found in {PAWLS_PAPERS_DIR}.")
        return

    logging.info(f"Found {len(paper_ids)} potential paper directories: {paper_ids}")

    for paper_id in paper_ids:
        process_paper(paper_id, PAWLS_PAPERS_DIR, OUTPUT_DIR)

    logging.info("Conversion script finished.")

if __name__ == "__main__":
    main() 