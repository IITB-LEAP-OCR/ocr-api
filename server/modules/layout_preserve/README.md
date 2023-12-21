# OCR API

## Overview

Implementation the OCR API involving integration of the Layout Preservation functionality from the Bhasini OCR API Repository. This integration will encompass different classes such as Tables, Equations, Figures, and Text to ensure the preservation of the document's layout during the optical character recognition process.

## Changes Integrated
### layout_preserve module
- The layout_preserve module has been introduced to centralize the code responsible for detecting and recognizing layout elements, including Tables, Equations, Figures, and Text. 

### routes.py
- The primary endpoint `/layout-preserve` has been introduced to facilitate layout preservation across various classes within the API.
- Users provide an image path, and the API returns a JSON response indicating the success or failure of the OCR process.

### helper.py
- `helper.py` includes code to perform layout detection and preservation.
- It encompasses several functions crucial for extracting the document layout, identifying and recognizing various classes, maintaining layout structure, and exporting OCR results in XML format.
- The `perform_ocr` function processes images, performs OCR, and generates hOCR (HTML-based OCR) output.
- The XML includes information about the page, blocks, lines, words, and their bounding boxes..

### models.py
- The code integrates layout analysis using layout parser models for detecting equations and figures in an image.
- The `create_model` function returns a Faster R-CNN model pre-trained on ResNet50 for table cell-wise classification.
- The `get_equation_recognition` function takes an image path, opens the image using PIL, and performs equation recognition using a pre-trained model `(LatexOCR)`.
- The `process_blocks_to_bboxes` function converts layout parser blocks into bounding boxes. This is used for both equation and figure detection.

### request_body.py
- It defines two Pydantic models, `OCRRequest` and `OCRResponse`, which are used for handling input parameters and output results in the OCR process.
- The `OCRRequest` includes fields for the image path, output set or document name, language for OCR, and a boolean indicating whether layout preservation (tables, figures, etc.) is desired in the HOCRs.
- The `OCRResponse` includes a list of strings representing the recognized text obtained from the OCR process.

## Input and Example JSON Response

**Input:**
- An image file path.
- Output set name or document name to be given to final result folder in output directory.
- Language to perform OCR.
- Boolean, True if we want to preserve tables, figures, etc. in the HOCRs.


**Example Input for layout_preservation = True**
```txt
{
    "image":"/home/user/Downloads/stats.pdf",
    "outputset_name":"TRY_NESTED",
    "language":"eng",
    "layout_preservation": true
}
```

**Example JSON Response for Success:**
```json
{
    "text": [
        "OCR SUCCESS and Pushed to repository: TRY_NESTED"
    ]
}
```