import pytesseract
import os
import cv2
import time
import shutil
import uuid
import requests
import torch
import warnings
import numpy as np
import layoutparser as lp
from os.path import join
from bs4 import BeautifulSoup
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from pdf2image import convert_from_path
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element as ETElement
from xml.etree.ElementTree import SubElement
warnings.filterwarnings('ignore')
from PIL import Image
from pix2tex.cli import LatexOCR
from .models import create_model
from .models import get_equation_detection
from .models import get_figure_detection
from fastapi import UploadFile
from torchvision.ops import nms



""" 
------------ SAVING UPLOADED IMAGE -------------
"""

# model path
faster_rcnn_model_path = "https://github.com/itsRenuka22/layout-parser-api/releases/download/table-detection/model700.pth"
# Server related directory paths
output_dir = '/home/user/Public/Projects/IITB/bhashini-ocr-api/src/output/' 
config_dir = "/home/user/Public/Projects/IITB/bhashini-ocr-api/src/config/"

def logtime(t: float, msg:  str) -> None:
	print(f'[{int(time.time() - t)}s]\t {msg}')

def save_uploaded_image(image: UploadFile) -> str:
	"""
	function to save the uploaded image to the disk

	@returns the absolute location of the saved image
	"""
	t = time.time()
	print('removing all the previous uploaded files from the image folder')
	os.system(f'rm -rf {input_file}/*')
	location = join(input_file, '{}.{}'.format(
		str(uuid.uuid4()),
		image.filename.strip().split('.')[-1]
	))
	with open(location, 'wb+') as f:
		shutil.copyfileobj(image.file, f)
	logtime(t, 'Time took to save one image')
	return location



# Returns true if two rectangles b1 and b2 overlap, b is of the form [x1, y1, x2, y2]
def do_overlap(b1, b2):
    if (b1[0] >= b2[2]) or (b1[2] <= b2[0]) or (b1[3] <= b2[1]) or (b1[1] >= b2[3]):
         return False
    else:
        return True
    

"""
-------- LAYOUT ----------
"""

#getting layout from a single image

""" Get most confident and non-overlapping bounding boxes """
def perform_nms(boxes, scores, nms_threshold):
    dets = torch.Tensor(boxes)
    scores = torch.Tensor(scores)
    res = nms(dets, scores, nms_threshold)
    final_boxes =[]
    for ind in res:
        final_boxes.append(boxes[ind])
    return final_boxes


""" Get tables and their cells """

def get_tables_cells_detection(img_file):
    # set the computation device
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    # load the model and the trained weights
    model = create_model(num_classes=3).to(device)
    response = requests.get(faster_rcnn_model_path)
    
    if response.status_code == 200:
        #Save downloaded content to file
        with open('model700.pth', 'wb') as model_file:
            model_file.write(response.content)

            #Load model.pth file using torch.load
            model.load_state_dict(torch.load('model700.pth', map_location=device))
    
    else:
        print("Failed to load model")

    model.eval()

    # classes: 0 index is reserved for background
    CLASSES = [
        'bkg', 'table', 'cell'
    ]
    # any classes having score below this will be discarded
    det_threshold = 0.5
    detection_threshold = det_threshold

    # get the image file name for saving output later on  (*** GETTING IMAGE FROM THE INPUT (MIGHT NEED TO EDIT) ***)
    image_name = img_file
    image = cv2.imread(image_name)
    orig_image = image.copy()
    # BGR to RGB
    image = cv2.cvtColor(orig_image, cv2.COLOR_BGR2RGB).astype(np.float32)
    # make the pixel range between 0 and 1
    image /= 255.0
    # bring color channels to front
    image = np.transpose(image, (2, 0, 1)).astype(float)
    # convert to tensor
    image = torch.tensor(image, dtype=torch.float)
    # add batch dimension
    image = torch.unsqueeze(image, 0)
    with torch.no_grad():
        outputs = model(image)

    # load all classes to CPU for further operations
    outputs = [{k: v.to('cpu') for k, v in t.items()} for t in outputs]
    # carry further only if there are detected boxes

    # Final lists to return
    tables = []
    cells = []

    #If bounding boxes are detected
    if len(outputs[0]['boxes']) != 0:
        #extract bboxes and scores
        boxes = outputs[0]['boxes'].data.numpy()
        scores = outputs[0]['scores'].data.numpy()
        # filter out boxes according to `detection_threshold`
        boxes = boxes[scores >= detection_threshold].astype(np.int32)
        draw_boxes = boxes.copy()    #boxes converted to integers and stored in draw_boxes
        # get all the predicted class names
        pred_classes = [CLASSES[i] for i in outputs[0]['labels'].cpu().numpy()]
        print('Table Prediction Complete')

        # Trim classes for top k boxes predicted over threshold score
        classes = pred_classes[:len(boxes)]

        # Collect table and cells 
        unfiltered_tables = []
        unfiltered_cells = []
        # Collect Scores
        table_scores = []
        cell_scores = []
        for i in range(len(boxes)):
            if classes[i] == 'table':
                unfiltered_tables.append(boxes[i])
                table_scores.append(scores[i])
            else:
                unfiltered_cells.append(boxes[i])
                cell_scores.append(scores[i])

        # Perform NMS to resolve overlap issue
        nms_table_threshold = 0.1
        nms_cell_threshold = 0.0001
        if len(unfiltered_tables):
            tables = perform_nms(unfiltered_tables, table_scores, nms_table_threshold)
        if len(unfiltered_cells):
            cells = perform_nms(unfiltered_cells, cell_scores, nms_cell_threshold)

    return tables, cells

""" Extract cells from table """
# tab --> bboxes of the table, cells --> list of cell bboxes
def get_cells_from_table(tab, cells):
    tablecells = []
    for c in cells:
        overlap = do_overlap(tab, c)
        if overlap:
            tablecells.append(c)
    return tablecells

""" Merge a list of bounding boxes into a single bounding box """    
def get_merged_cell(final_cells):
    if len(final_cells) == 1:
        return final_cells[0]
    x1 = [c[0] for c in final_cells]
    y1 = [c[1] for c in final_cells]
    x2 = [c[2] for c in final_cells]
    y2 = [c[3] for c in final_cells]
    cell = [min(x1), min(y1), max(x2), max(y2)]
    return cell

""" Retrieve the final (merged) bounding box for a specific cell in a table"""
def get_final_cell(tablecellrows, skeleton, rowindex, colindex):
    final_cells = []
    row_to_consider = tablecellrows[rowindex]
    col_skeleton = skeleton[rowindex]
    assert len(row_to_consider) == len(col_skeleton)
    for i in range(len(col_skeleton)):
        if col_skeleton[i] == colindex:
            final_cells.append(row_to_consider[i])
    if len(final_cells) == 0:
        return []
    else:
        final_cell = get_merged_cell(final_cells)
    return final_cell

""" Processes a set of detected tables and cells, extracting structured information about the tables and their cell contents. """
def get_table_response_from_page(tables, cells):
    full_table_response = []
    row_determining_threshold = 0.6667
    for tablebbox in tables:
        tabcells = get_cells_from_table(tablebbox, cells) 

        # Proceed only if table has cells
        if len(tabcells) > 0:
            # Sort cells based on y coordinates
            strcells = sorted(tabcells, key=lambda b: b[1] + b[3], reverse=False)

            # Calculate Mean height -- assist in determining rows
            cell_heights = [c[3] - c[1] for c in tabcells]
            mean_height = int(np.mean(cell_heights))

            # Assign row to each cell based on y coordinate wise arrangement
            cellrow = [0]
            assign_row = 0
            for i in range(len(strcells) - 1):
                consec_cell_height = strcells[i + 1][1] - strcells[i][1]
                if consec_cell_height > row_determining_threshold * mean_height:
                    assign_row = assign_row + 1
                cellrow.append(assign_row)

            # Get number of rows and columns
            rows = list(set(cellrow))
            nrows = len(rows)
            counts = [0] * nrows
            for cr in cellrow:
                counts[cr] = counts[cr] + 1
            ncols = max(counts)

            # Generate row-wise cell sequences of bounding boxes
            cellrows = {}
            for i in rows:
                row_wise_cells = []
                for j in range(len(strcells)):
                    if i == cellrow[j]:
                        row_wise_cells.append(strcells[j])
                row_wise_cells = sorted(row_wise_cells, key=lambda b: b[0], reverse=False)
                cellrows[i] = row_wise_cells

            tableresponse = {}
            tableresponse['bbox'] = tablebbox
            tableresponse['nrows'] = nrows
            tableresponse['ncells'] = len(strcells)
            tableresponse['cellrows'] = cellrows
            full_table_response.append(tableresponse)
    return full_table_response


""" Extracting text"""
def get_cell_text(image, cellbbox, lang):
    cropped_image = image[cellbbox[1]:cellbbox[3], cellbbox[0]:cellbbox[2]]
    text = pytesseract.image_to_string(cropped_image, lang=lang, config='--psm 6')
    return text


""" Generating HOCR for the input table"""
def get_hocr_from_table_response(imgfile, tableresponse, lang):
    raw_image = cv2.imread(imgfile)
    nrows = tableresponse['nrows']
    tablecellrows = tableresponse['cellrows']
    tablebbox = tableresponse['bbox']
    col_determining_threshold = 0.5
    #lang = table_recognition_language

    # Preparing skeleton to assign column numbers
    final_skeleton = []
    max_entries_per_row = []
    for row in tablecellrows:
        row_to_consider = tablecellrows[row]
        # Calculate Mean height
        cell_widths = [c[3] - c[1] for c in row_to_consider]
        mean_width = int(np.mean(cell_widths))
        # Sort cells in same row from left to right
        ltor_cells = sorted(row_to_consider, key=lambda b:b[0], reverse=False)
        # Assign col number to every cell
        col_to_assign = 0
        assigned_col = [0]
        for i in range(len(ltor_cells) - 1):
            consec_cell_diff = ltor_cells[i + 1][0] - ltor_cells[i][0]
            if consec_cell_diff > col_determining_threshold * mean_width:
                col_to_assign = col_to_assign + 1
            assigned_col.append(col_to_assign)
        max_entries_per_row.append(col_to_assign)
        final_skeleton.append(assigned_col)
        
    ncols = max(max_entries_per_row)  + 1

    # HOCR Generation
    hocr = '<table class="ocr_tab" border=1 style="margin: 0px auto; text-align: center;"'
    tabbbox = " ".join(tablebbox.astype(str))
    hocr = hocr + f' title = "bbox {tabbbox}" >'
    for i in range(nrows):
        hocr = hocr + '<tr>'
        for j in range(ncols):
            cell = get_final_cell(tablecellrows, final_skeleton, i, j)
            if len(cell) == 4:
                cellbbox = str(cell[0]) + ' ' + str(cell[1]) + ' '  + str(cell[2]) + ' ' + str(cell[3])
                cellattribute = f' title = "bbox {cellbbox}"'
            else:
                cellattribute = ''
            if len(cell) == 0:
                text = ''
            else :
                text = get_cell_text(raw_image, cell, lang)
            hocr = hocr + f'<td {cellattribute} >' + text + '</td>' 
        hocr = hocr + '</tr>'
    hocr = hocr + '</table>'
    entry = []
    entry.append(hocr)
    entry.append(tablebbox)
    return entry


""" Considering entire page and generating HOCR """
def get_table_hocrs(imgfile, table, cells, lang):
    full_table_response = get_table_response_from_page(table, cells)
    full_hocrs_response = []
    if len(full_table_response):
        for table_response in full_table_response:
            hocr = get_hocr_from_table_response(imgfile, table_response, lang)
            full_hocrs_response.append(hocr)
    return full_hocrs_response


""" 
--------- LAYOUT FOR FIGURE AND EQUATION ----------
"""

def mask_image(image, boxes):
    for b in boxes:
        cv2.rectangle(image, (b[0], b[1]), (b[2],b[3]), (255, 255, 255), -1)
    return image


def get_layout_from_single_image(image_name):
    layout = {}
    image = cv2.imread(image_name)
    height, width, _ = image.shape
    table_bboxes, cell_bboxes = get_tables_cells_detection(image_name)
    masked_image = mask_image(image, table_bboxes)
    equation_bboxes = get_equation_detection(masked_image)
    masked_image = mask_image(image, equation_bboxes)
    figure_bboxes = get_figure_detection(masked_image)
    layout['image-name'] = image_name
    layout['height'] = height
    layout['width'] = width
    layout['tables'] = table_bboxes
    layout['cells'] = cell_bboxes
    layout['equations'] = equation_bboxes
    layout['figures'] = figure_bboxes
    layout['masked-image'] = masked_image
    return layout


"""
--------- FIGURE ------------

"""

def get_figure_hocrs(image, figure_bboxes, outputDirectory, pagenumber):
    result = []
    for count, fig in enumerate(figure_bboxes):
        cropped_image = image[fig[1]: fig[3], fig[0]: fig[2]]
        image_file_name = '/Cropped_Images/figure_' + str(pagenumber) + '_' + str(count) + '.jpg'
        cv2.imwrite(outputDirectory + image_file_name, cropped_image)
        imagehocr = f"<img class=\"ocr_im\" title=\"bbox {fig[0]} {fig[1]} {fig[2]} {fig[3]}\" src=\"../{image_file_name}\">"
        result.append([imagehocr, fig])
    return result


"""
----- EQUATIONS -------

"""
LatexModelEquation = LatexOCR()

#Perform equation recognition and get equation HOCRS
def get_equation_recognition(image_path):
    img_pil = Image.open(image_path)
    return LatexModelEquation(img_pil)

""" Generate HOCR FOR EQUATION """
def get_equation_hocrs(image, equation_bboxes, outputDirectory, pagenumber):
    result = []
    for count, fig in enumerate(equation_bboxes):
        cropped_image = image[fig[1]: fig[3], fig[0]: fig[2]]
        image_file_name = '/Cropped_Images/equation_' + str(pagenumber) + '_' + str(count) + '.jpg'
        cv2.imwrite(outputDirectory + image_file_name, cropped_image)
        equation_recog = get_equation_recognition(outputDirectory + image_file_name)
        eqnhocr = f'<span class=\"ocr_eq\" title=\"bbox {fig[0]} {fig[1]} {fig[2]} {fig[3]}\">{equation_recog}</span>'
        result.append([eqnhocr, fig])
    return result



""" 
---------- PERFORMING OCR ------------

"""

def perform_ocr(orig_pdf_path, project_folder_name, lang, ocr_only, layout_preservation, nested_ocr, pdftoimg):
    # Set output directories
    global input_file
    input_file= orig_pdf_path
    outputDirIn = output_dir
    outputDirectory = outputDirIn + project_folder_name
    imagesFolder = outputDirectory + "/Images"
    individualOutputDir = outputDirectory + "/Inds"
    create_output_set(orig_pdf_path, outputDirectory, pdftoimg)
    os.system('cp '+ config_dir + 'project.xml ' + outputDirectory)
    # os.system('cp ../../dicts/* ' + outputDirectory + "/Dicts/")
    print("Selected language model " + lang)
    os.environ['CHOSENMODEL'] = lang

    if pdftoimg == 'pdf2img':
        exit(0)

    # Start recording OCR time
    startOCR = time.time()

    for imfile in os.listdir(imagesFolder):
        # finalimgtoocr refers to the full path of the image which will be fed to OCR framework.
        # finalimgtoocr will be a masked image if layout preservation is to be carried out where graphical objects are hidden
        finalimgtoocr = imagesFolder + "/" + imfile

        # Determining page number from file name
        dash = imfile.index('-')
        dot = imfile.index('.')
        page = int(imfile[dash + 1 : dot])

        # Graphical document object data initialized
        figuredata = []
        tabledata = []
        equationsdata = []

        if nested_ocr:
            # Because for Nested OCR we must include layout so that flag is made true, txt files will be later written using docTR detection
            doctr_model = ocr_predictor(pretrained=True)
            layout_preservation = True
        else:
            # Write txt files for all pages using Tesseract
            txt = pytesseract.image_to_string(imagesFolder + "/" + imfile, lang=lang)
            with open(individualOutputDir + '/' + imfile[:-3] + 'txt', 'w') as f:
                f.write(txt)

        # Get tables and figures if request is to preserve the layout
        if layout_preservation:
            # Get page layout
            page_layout = get_layout_from_single_image(finalimgtoocr)

            # Get tables from faster rcnn predictions in hocr format
            fullpathimgfile = imagesFolder + '/' + imfile
            tables = page_layout['tables']
            cells = page_layout['cells']
            tabledata = get_table_hocrs(fullpathimgfile, tables, cells, lang)
            print(str(fullpathimgfile) + ' has ' + str(len(tabledata)) + ' tables extracted')

            # Perform figure detection from page image to get their hocrs and bounding boxes
            img = cv2.imread(imagesFolder + "/" + imfile)
            figures = page_layout['figures']
            figuredata = get_figure_hocrs(img, figures, outputDirectory, page)

            # Equation Recognition 
            equations = page_layout.get('equations', [])
            if equations != []:
                equationsdata = get_equation_hocrs(img, equations, outputDirectory, page)

            # For layout, we OCR the masked image after hiding graphical document objects
            masked_image = page_layout['masked-image']
            masked_img_filename = outputDirectory + "/MaskedImages/" + imfile[:-4] + '_filtered.jpg'
            cv2.imwrite(masked_img_filename, masked_image)
            finalimgtoocr = masked_img_filename

        # Creating final HOCRs
        if nested_ocr:
            # For nested OCR, hocr is created using doctr
            print('We will OCR the image in a nested fashion ' + finalimgtoocr)
            hocr = perform_nested_ocr(finalimgtoocr, doctr_model, imfile,  individualOutputDir, lang)
        else:
            # Else, we create hocr using Tesseract
            print('We will OCR this image using Tesseract => ' + finalimgtoocr)
            hocr = pytesseract.image_to_pdf_or_hocr(finalimgtoocr, lang=lang, extension='hocr')

        # Parsing the hocr to add tables, figures in proper place
        soup = BeautifulSoup(hocr, 'html.parser')
        # Adding table hocr in final hocr at proper position
        if len(tabledata) > 0:
            for entry in tabledata:
                tab_tag = entry[0]
                tab_element = BeautifulSoup(tab_tag, 'html.parser')
                # print(tab_tag)
                tab_bbox = entry[1]
                # y-coordinate
                tab_position = tab_bbox[1]
                for elem in soup.find_all('span', class_="ocr_line"):
                    find_all_ele = elem.attrs["title"].split(" ")
                    line_position = int(find_all_ele[2])
                    if tab_position < line_position:
                        elem.insert_before(tab_element)
                        break

        # Adding image hocr in final hocr at proper position
        if len(figuredata) > 0:
            for image_details in figuredata:
                imghocr = image_details[0]
                img_element = BeautifulSoup(imghocr, 'html.parser')
                img_position = image_details[1][1]
                for elem in soup.find_all('span', class_="ocr_line"):
                    find_all_ele = elem.attrs["title"].split(" ")
                    line_position = int(find_all_ele[2])
                    if img_position < line_position:
                        elem.insert_before(img_element)
                        break

        # Adding equation hocr in final hocr at proper position
        if len(equationsdata) > 0:
            for eqn_details in equationsdata:
                eqn_hocr = eqn_details[0]
                eqn_element = BeautifulSoup(eqn_hocr, 'html.parser')
                eqn_position = eqn_details[1][1]
                for elem in soup.find_all('span', class_="ocr_line"):
                    find_all_ele = elem.attrs["title"].split(" ")
                    line_position = int(find_all_ele[2])
                    if eqn_position < line_position:
                        elem.insert_before(eqn_element)
                        break

        # Write final hocrs in the 'Inds' directory
        hocrfile = individualOutputDir + '/' + imfile[:-3] + 'hocr'
        f = open(hocrfile, 'w+')
        f.write(str(soup))

    # Generate HTMLS in Corrector Output if OCR ONLY
    if(ocr_only):
        copy_command = 'cp {}/*.hocr {}/'.format(individualOutputDir, outputDirectory + "/CorrectorOutput")
        os.system(copy_command)
        correctorFolder = outputDirectory + "/CorrectorOutput"
        for hocrfile in os.listdir(correctorFolder):
            if "hocr" in hocrfile:
                htmlfile = hocrfile.replace(".hocr", ".html")
                os.rename(correctorFolder + '/' + hocrfile, correctorFolder + '/' + htmlfile)

    # Calculate the time elapsed for entire OCR process
    endOCR = time.time()
    ocr_duration = round((endOCR - startOCR), 3)
    print('Done with OCR of ' + str(project_folder_name) + ' of ' + str(len(os.listdir(imagesFolder))) + ' pages in ' + str(ocr_duration) + ' seconds')
    #push output_setname to certain git repo
    return ("OCR SUCCESS and Pushed to repository: " + project_folder_name)


""" If we want to perform NESTED OCR (DocTR recognition after Pytersseract) """

def perform_nested_ocr(finalimgtoocr, doctr_model, img_filename,  individualOutputDir, lang):
    img = cv2.imread(finalimgtoocr)
    doc = DocumentFile.from_images(finalimgtoocr)
    result = doctr_model(doc)
    text_file_content = ''
    for page in result.pages:
        height, width = page.dimensions
        for block in page.blocks:
            for line in block.lines:
                for word in line.words:
                    ((x1, y1), (x2, y2)) = word.geometry
                    x1 = int(x1 * width)
                    x2 = int(x2 * width)
                    y1 = int(y1 * height)
                    y2 = int(y2 * height)
                    bb = ((x1, y1), (x2, y2))
                    # Crop the block
                    cropped_image = img[bb[0][1]:bb[1][1], bb[0][0]:bb[1][0]]
                    # Perform OCR
                    text = pytesseract.image_to_string(cropped_image, lang=lang)
                    text_file_content = text_file_content + ' ' + text
                    word.value = text

    page_result = result.pages[0]
    hocr_file_content = export_as_xml(page_result)

    # Write final txt
    txtfile = individualOutputDir + '/' + img_filename[:-3] + 'txt'
    f = open(txtfile, 'w+')
    f.write(text_file_content)
    f.close()
    # Write final hocrs
    hocrfile = individualOutputDir + '/' + img_filename[:-3] + 'hocr'
    f = open(hocrfile, 'w+')
    f.write(hocr_file_content)
    f.close()
    return hocr_file_content


""" 
------------ EXPORTING IN XML FORMAT -------------

"""

def export_as_xml(self, file_title: str = "docTR - XML export (hOCR)"):
    """Export the page as XML (hOCR-format)
    convention: https://github.com/kba/hocr-spec/blob/master/1.2/spec.md

    Args:
        file_title: the title of the XML file

    Returns:
        a tuple of the XML byte string, and its ElementTree
    """
    p_idx = 1
    block_count: int = 1
    line_count: int = 1
    word_count: int = 1
    height, width = self.dimensions
    language = self.language if "language" in self.language.keys() else "en"
    # Create the XML root element
    page_hocr = ETElement("html", attrib={"xmlns": "http://www.w3.org/1999/xhtml", "xml:lang": str(language)})
    # Create the header / SubElements of the root element
    head = SubElement(page_hocr, "head")
    SubElement(head, "title").text = file_title
    SubElement(head, "meta", attrib={"http-equiv": "Content-Type", "content": "text/html; charset=utf-8"})
    SubElement(
        head,
        "meta",
        attrib={"name": "ocr-system", "content": "python-doctr"},  # type: ignore[attr-defined]
    )
    SubElement(
        head,
        "meta",
        attrib={"name": "ocr-capabilities", "content": "ocr_page ocr_carea ocr_par ocr_line ocrx_word"},
    )
    # Create the body
    body = SubElement(page_hocr, "body")
    SubElement(
        body,
        "div",
        attrib={
            "class": "ocr_page",
            "id": f"page_{p_idx + 1}",
            "title": f"image; bbox 0 0 {width} {height}; ppageno 0",
        },
    )
    # iterate over the blocks / lines / words and create the XML elements in body line by line with the attributes
    for block in self.blocks:
        if len(block.geometry) != 2:
            raise TypeError("XML export is only available for straight bounding boxes for now.")
        (xmin, ymin), (xmax, ymax) = block.geometry
        block_div = SubElement(
            body,
            "div",
            attrib={
                "class": "ocr_carea",
                "id": f"block_{block_count}",
                "title": f"bbox {int(round(xmin * width))} {int(round(ymin * height))} \
                {int(round(xmax * width))} {int(round(ymax * height))}",
            },
        )
        paragraph = SubElement(
            block_div,
            "p",
            attrib={
                "class": "ocr_par",
                "id": f"par_{block_count}",
                "title": f"bbox {int(round(xmin * width))} {int(round(ymin * height))} \
                {int(round(xmax * width))} {int(round(ymax * height))}",
            },
        )
        block_count += 1
        for line in block.lines:
            (xmin, ymin), (xmax, ymax) = line.geometry
            # NOTE: baseline, x_size, x_descenders, x_ascenders is currently initalized to 0
            line_span = SubElement(
                paragraph,
                "span",
                attrib={
                    "class": "ocr_line",
                    "id": f"line_{line_count}",
                    "title": f"bbox {int(round(xmin * width))} {int(round(ymin * height))} \
                    {int(round(xmax * width))} {int(round(ymax * height))}; \
                    baseline 0 0; x_size 0; x_descenders 0; x_ascenders 0",
                },
            )
            line_count += 1
            for word in line.words:
                (xmin, ymin), (xmax, ymax) = word.geometry
                conf = word.confidence
                word_div = SubElement(
                    line_span,
                    "span",
                    attrib={
                        "class": "ocrx_word",
                        "id": f"word_{word_count}",
                        "title": f"bbox {int(round(xmin * width))} {int(round(ymin * height))} {int(round(xmax * width))} {int(round(ymax * height))}; x_wconf {int(round(conf * 100))}",
                    },
                )
                # set the text
                word_div.text = word.value
                word_count += 1

    return ET.tostring(page_hocr, encoding="unicode", method="xml")

def parse_boolean(b):
    return b == "True"

# for simpler filename generation
def simple_counter_generator(prefix="", suffix=""):
    i = 400
    while True:
        i += 1
        yield 'p'

def create_output_set(orig_pdf_path, outputDirectory, pdftoimg):
    print('output directory is ', outputDirectory)
    # create images,text folder
    print('cwd is ', os.getcwd())
    if not os.path.exists(outputDirectory):
        os.mkdir(outputDirectory)
    if not os.path.exists(outputDirectory + "/Images"):
        os.mkdir(outputDirectory + "/Images")
    imagesFolder = outputDirectory + "/Images"
    imageConvertOption = 'True'
    print("converting pdf to images")
    jpegopt = {
        "quality": 100,
        "progressive": True,
        "optimize": False
    }
    output_file = simple_counter_generator("page", ".jpg")
    print('orig pdf oath is', orig_pdf_path)
    print('cwd is', os.getcwd())
    print("orig_pdf_path is", orig_pdf_path)
    if (parse_boolean(imageConvertOption)):
        convert_from_path(orig_pdf_path, output_folder=imagesFolder, dpi=300, fmt='jpeg', jpegopt=jpegopt,
                          output_file=output_file)
    print("images created.")
    print(pdftoimg)
    if pdftoimg != 'pdf2img':
        print("Now we will OCR")
        os.environ['IMAGESFOLDER'] = imagesFolder
        # os.environ['CWD']='/home/sanskar/udaan-deploy-pipeline'
        os.environ['OUTPUTDIRECTORY'] = outputDirectory
        # os.environ['CHOSENFILENAMEWITHNOEXT']=chosenFileNameWithNoExt
        # os.system('find $IMAGESFOLDER -maxdepth 1 -type f > $OUTPUTDIRECTORY/tmp.list')
        # tessdata_dir_config = r'--tessdata-dir "$/home/sanskar/NLP-Deployment-Heroku/udaan-deploy-pipeline/tesseract-exec/tessdata/"'
        tessdata_dir_config = r'--psm 3 --tessdata-dir "/home/ayush/udaan-deploy-flask/udaan-deploy-pipeline/tesseract-exec/share/tessdata/"'
        tessdata_dir_config = r'--psm 3 --tessdata-dir "/usr/share/tesseract-ocr/4.00/tessdata/"'
        tessdata_dir_config = r'--tessdata-dir "/home/ayush/udaan-deploy-flask/udaan-deploy-pipeline/tesseract-exec/share/tessdata/"'
        languages = pytesseract.get_languages(config=tessdata_dir_config)
        lcount = 0
        tesslanglist = {}
        for l in languages:
            if not (l == 'osd'):
                tesslanglist[lcount] = l
                lcount += 1
                print(str(lcount) + '. ' + l)

    if not os.path.exists(outputDirectory + "/CorrectorOutput"):
        os.mkdir(outputDirectory + "/CorrectorOutput")
        os.mknod(outputDirectory + "/CorrectorOutput/" + 'README.md', mode=0o666)

    # Creating Final set folders and files
    if not os.path.exists(outputDirectory + "/Comments"):
        os.mkdir(outputDirectory + "/Comments")
        os.mknod(outputDirectory + "/Comments/" + 'README.md', mode=0o666)
    if not os.path.exists(outputDirectory + "/VerifierOutput"):
        os.mkdir(outputDirectory + "/VerifierOutput")
        os.mknod(outputDirectory + "/VerifierOutput/" + 'README.md', mode=0o666)
    if not os.path.exists(outputDirectory + "/Inds"):
        os.mkdir(outputDirectory + "/Inds")
        os.mknod(outputDirectory + "/Inds/" + 'README.md', mode=0o666)
    if not os.path.exists(outputDirectory + "/Dicts"):
        os.mkdir(outputDirectory + "/Dicts")
        os.mknod(outputDirectory + "/Dicts/" + 'README.md', mode=0o666)
    if not os.path.exists(outputDirectory + "/Cropped_Images"):
        os.mkdir(outputDirectory + "/Cropped_Images")
    if not os.path.exists(outputDirectory + "/MaskedImages"):
        os.mkdir(outputDirectory + "/MaskedImages")
    return
