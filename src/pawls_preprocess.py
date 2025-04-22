from typing import Tuple
import csv
import io

from pathlib import Path
import os
import glob
from tqdm import tqdm
import hashlib
import shutil
import json

import pytesseract
import pandas as pd
from pdf2image import convert_from_path

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import resolve1

from model import Page

def hash_pdf(file) -> str:
    block_size = 65536

    file_hash = hashlib.sha256()
    with open(str(file), 'rb') as fp:
        fb = fp.read(block_size)
        while len(fb) > 0:
            file_hash.update(fb)
            fb = fp.read(block_size)

    return str(file_hash.hexdigest())

def copy(source, destination) -> None:
    shutil.copy(str(source), str(destination))

def add_hash(directory, out_dir) -> None:
    """
    Add a PDF or directory of PDFs to the pawls dataset (skiff_files/).
    """
    base_dir = Path(out_dir / "skiff_files/apps/pawls/papers")
    base_dir.mkdir(exist_ok=True, parents=True)

    if os.path.isdir(str(directory)):
        pdfs = glob.glob(os.path.join(str(directory), "*.pdf"))
    else:
        pdfs = [str(directory)]

    for pdf in tqdm(pdfs):
        pdf_name = Path(pdf).stem

        output_dir = base_dir / pdf_name

        if output_dir.exists():
            print(f"PDF with name {pdf_name}.pdf already added. Skipping...")
            continue

        output_dir.mkdir(exist_ok=True)

        copy(pdf, output_dir / (pdf_name + '.pdf'))

def preprocess(path):
    """
    Run a pre-processor on a pdf/directory of pawls pdfs and
    write the resulting token information to the pdf location.

    Current preprocessor options are: "grobid".

    To send all pawls structured pdfs in the current directory for processing:

        `pawls preprocess grobid ./`
    """
    if os.path.isdir(path):
        in_glob = os.path.join(path, "*/*.pdf")
        pdfs = glob.glob(in_glob)
    else:
        if not str(path).endswith(".pdf"):
            raise ValueError("Path is not a directory, but also not a pdf.")
        pdfs = [str(path)]

    pbar = tqdm(pdfs)

    for p in pbar:
        path = Path(p)
        pbar.set_description(f"Processing {path}")
        data = process_tesseract(str(path))
        with open(path.parent / "pdf_structure.json", "w+") as f:
            json.dump(data, f)


def assign(
    path
):
    shas = set()

    pdfs = glob.glob(os.path.join(path, "*/*.pdf"))
    project_shas = {p.split("/")[-2] for p in pdfs}

    shas.update(project_shas)

    status_dir = os.path.join(path, "status")
    os.makedirs(status_dir, exist_ok=True)

    status_path = os.path.join(status_dir, "development_user@example.com.json")

    pdf_status = {}
    for sha in sorted(shas):
            name = sha

            pdf_status[sha] = {
                "sha": sha,
                "name": name,
                "annotations": 0,
                "relations": 0,
                "finished": False,
                "junk": False,
                "comments": "",
                "completedAt": None,
            }

    with open(status_path, "w+") as out:
        json.dump(pdf_status, out)

def calculate_image_scale_factor(pdf_size, image_size):
    pdf_w, pdf_h = pdf_size
    img_w, img_h = image_size
    scale_w, scale_h = pdf_w / img_w, pdf_h / img_h
    return scale_w, scale_h


def get_pdf_pages_and_sizes(filename: str):
    """Ref https://stackoverflow.com/a/47686921"""
    with open(filename, "rb") as fp:
        parser = PDFParser(fp)
        document = PDFDocument(parser)
        num_pages = resolve1(document.catalog["Pages"])["Count"]
        page_sizes = [
            (int(page.mediabox[2]), int(page.mediabox[3]))
            for page in PDFPage.create_pages(document)
        ]
        return num_pages, page_sizes



def extract_page_tokens(
    pdf_image: "PIL.Image", pdf_size=Tuple[float, float], language="eng"
) -> list[dict]:

    _data = pytesseract.image_to_data(pdf_image, lang=language)

    scale_w, scale_h = calculate_image_scale_factor(pdf_size, pdf_image.size)

    res = pd.read_csv(
        io.StringIO(_data), quoting=csv.QUOTE_NONE, encoding="utf-8", sep="\t"
    )
    # An implementation adopted from https://github.com/Layout-Parser/layout-parser/blob/20de8e7adb0a7d7740aed23484fa8b943126f881/src/layoutparser/ocr.py#L475
    tokens = (
        res[~res.text.isna()]
        .groupby(["page_num", "block_num", "par_num", "line_num", "word_num"])
        .apply(
            lambda gp: pd.Series(
                [
                    gp["left"].min(),
                    gp["top"].min(),
                    gp["width"].max(),
                    gp["height"].max(),
                    gp["conf"].mean(),
                    gp["text"].astype(str).str.cat(sep=" "),
                ]
            )
        )
        .reset_index(drop=True)
        .reset_index()
        .rename(
            columns={
                0: "x",
                1: "y",
                2: "width",
                3: "height",
                4: "score",
                5: "text",
                "index": "id",
            }
        )
        .drop(columns=["score", "id"])
        .assign(
            x=lambda df: df.x * scale_w,
            y=lambda df: df.y * scale_h,
            width=lambda df: df.width * scale_w,
            height=lambda df: df.height * scale_h,
        )
        .apply(lambda row: row.to_dict(), axis=1)
        .tolist()
    )

    return tokens


def parse_annotations(pdf_file: str) -> list[Page]:
    pdf_images = convert_from_path(pdf_file)
    _, pdf_sizes = get_pdf_pages_and_sizes(pdf_file)
    pages = []
    pbar = tqdm(enumerate(zip(pdf_images, pdf_sizes)))
    for page_index, (pdf_image, pdf_size) in pbar:
        pbar.set_description(f"Processing page {page_index}")
        tokens = extract_page_tokens(pdf_image, pdf_size)
        w, h = pdf_size
        page = dict(
            page=dict(
                width=w,
                height=h,
                index=page_index,
            ),
            tokens=tokens,
        )
        pages.append(page)

    return pages


def process_tesseract(pdf_file: str):
    """
    Integration for importing annotations from pdfplumber.
    pdf_file: str
        The path to the pdf file to process.
    """
    annotations = parse_annotations(pdf_file)

    return annotations
