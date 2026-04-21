---
name: pdf-ocr-to-docx
description: Convert scanned/image-based PDFs to editable Word documents via OCR. TRIGGER when: user asks to OCR a PDF, convert scanned PDF to Word/DOCX, extract text from image-based PDFs, or convert Arabic/RTL PDFs. Also triggers when PDF text extraction returns garbled text or empty strings.
---

# PDF OCR to DOCX Conversion

Convert scanned or image-based PDFs into editable Word documents using vision-based OCR. This skill handles the full pipeline: PDF analysis → page-to-image conversion → vision OCR → DOCX generation.

## When to Use

- PDF text extraction returns garbled/empty text (image-based PDF)
- User wants an **editable** DOCX from a scanned PDF
- PDF contains Arabic, Hebrew, or other RTL text
- User mentions OCR, scanned documents, or image PDFs

## Workflow Overview

```
PDF → Analyze → Convert pages to PNG → Vision OCR each page → Build DOCX
```

## Step 1: Analyze the PDF

Determine if the PDF is image-based (needs OCR) or has extractable text.

```python
import pypdf

reader = pypdf.PdfReader("input.pdf")
page_count = len(reader.pages)
sample_text = reader.pages[0].extract_text()

if not sample_text or len(sample_text.strip()) < 10:
    print("Image-based PDF — OCR required")
else:
    print("Text-based PDF — direct extraction possible")
```

If text extraction works, you may not need this skill — use direct conversion instead.

## Step 2: For Large PDFs, Propose a Test Run

For PDFs with more than 20 pages, propose testing with the first 15–20 pages before processing the full document. This lets the user verify quality before committing to a long OCR session.

## Step 3: Convert PDF Pages to Images

Use `pypdfium2` to render each page to a PNG image at high resolution:

```python
import pypdfium2 as pdfium
import os

def convert_pages_to_images(pdf_path, output_dir, start_page=0, end_page=None):
    """Convert PDF pages to PNG images for OCR."""
    os.makedirs(output_dir, exist_ok=True)
    pdf = pdfium.PdfDocument(pdf_path)
    
    if end_page is None:
        end_page = len(pdf)
    
    for i in range(start_page, end_page):
        page = pdf[i]
        bitmap = page.render(scale=2)  # 2x for better OCR quality
        pil_image = bitmap.to_pil()
        img_path = os.path.join(output_dir, f"page_{i+1:03d}.png")
        pil_image.save(img_path)
        print(f"Saved: {img_path}")
    
    pdf.close()
```

**Dependencies:** Install with `pip install pypdfium2 Pillow` if not available.

## Step 4: OCR Each Page with Vision

Use the `view_file` tool to read each page image. This is the core OCR step.

**Critical instructions for vision OCR:**

1. View each page image with `view_file`
2. Transcribe **ALL** text exactly as it appears, including:
   - **Diacritical marks (tashkeel)** for Arabic: فَتْحَة، ضَمَّة، كَسْرَة، شَدَّة، سُكُون، تَنْوِين
   - Footnotes and references at the bottom
   - Section separators (e.g., `* * *`)
   - Page numbers (note them but don't include in text)
3. Save OCR'd text into a structured text file using page delimiters:

```
===PAGE 1===
[transcribed text for page 1]

===PAGE 2===
[transcribed text for page 2]
```

**For Arabic/RTL text:** Pay extreme attention to every diacritical mark. The tashkeel is critical for readability and correct pronunciation. Every fatḥa (َ), kasra (ِ), ḍamma (ُ), shadda (ّ), sukūn (ْ), and tanwīn must be captured.

**Batch strategy:** Process 5 pages at a time using parallel `view_file` calls, then save the batch to the text file before proceeding.

## Step 5: Build the DOCX

Use the bundled `scripts/build_docx.py` script to generate the DOCX from the OCR text files.

```bash
python <skill-path>/scripts/build_docx.py \
  --input pages_text.txt \
  --output output.docx \
  --font "Sakkal Majalla" \
  --font-size 16 \
  --direction rtl
```

**Arguments:**
- `--input`: Path(s) to OCR text file(s). Can specify multiple: `--input file1.txt file2.txt`
- `--output`: Output DOCX path
- `--font`: Font name (default: `Sakkal Majalla` for Arabic, `Calibri` for LTR)
- `--font-size`: Body text size in points (default: 16)
- `--direction`: `rtl` or `ltr` (default: auto-detect from text content)
- `--title-pages`: Number of initial pages to treat as title/cover pages (default: 6)
- `--chapter-titles`: Comma-separated list of chapter title strings to format as headings

If the script is not available, read `scripts/build_docx.py` and follow the same pattern to create the DOCX manually using `python-docx`.

## Language-Specific Notes

### Arabic Text
- **Font:** Use `Sakkal Majalla` (clean, modern, readable) — pre-installed on Windows
- **Fallbacks:** `Traditional Arabic`, `Simplified Arabic`, `Amiri`
- **Tashkeel:** Never skip diacritical marks. They are essential
- **RTL:** Must set bidi at document, section, paragraph, AND run levels

### Latin/LTR Text
- **Font:** Use `Calibri` or `Times New Roman`
- **Direction:** LTR (default)

### Mixed Content
- Set document direction based on the majority language
- Individual paragraphs can override direction

## Troubleshooting

| Issue | Solution |
|-------|---------|
| `pypdfium2` not installed | `pip install pypdfium2 Pillow` |
| `python-docx` not installed | `pip install python-docx lxml` |
| Text appears LTR in Word | Check RTL is set at ALL levels (doc, section, para, run) |
| Missing tashkeel | Re-OCR the page, explicitly requesting all diacritical marks |
| File permission error | Save to a new filename if the old file is open in Word |
| Garbled text from pypdf | PDF is image-based — proceed with OCR workflow |
