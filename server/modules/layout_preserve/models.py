from PIL import Image
import layoutparser as lp
from pix2tex.cli import LatexOCR
import torchvision
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor



# Returns Faster RCNN model to perfrom table cell-wise classes
def create_model(num_classes):
    # load Faster RCNN pre-trained model
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)    
    # get the number of input features 
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    # define a new head for the detector with required number of classes
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes) 
    return model

""" 
-------- EQUATION TEXT RECOGNITION ----------
"""

def process_blocks_to_bboxes(lp_blocks):
    bboxes = []
    blocks = lp_blocks.to_dict()['blocks']
    for blk in blocks:
        box = [int(blk['x_1']), int(blk['y_1']), int(blk['x_2']), int(blk['y_2'])]
        bboxes.append(box)
    return bboxes


def get_equation_detection(image):
    # MFD Model Equations
    model = lp.Detectron2LayoutModel(
        config_path='https://www.dropbox.com/s/ld9izb95f19369w/config.yaml?dl=1',  # In model catalog
        label_map={1: "Equation"},  # In model`label_map`
        extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8]  # Optional
    )
    layout = model.detect(image)
    equation_blocks = lp.Layout([b for b in layout if b.type == 'Equation'])
    equation_bboxes = process_blocks_to_bboxes(equation_blocks)
    return equation_bboxes

LatexModelEquation = LatexOCR()

def get_equation_recognition(image_path):
    img_pil = Image.open(image_path)
    return LatexModelEquation(img_pil)

def get_figure_detection(image):
    # Layout
    model = lp.Detectron2LayoutModel(
        config_path='https://www.dropbox.com/s/yc92x97k50abynt/config.yaml?dl=1',  # In model catalog
        label_map={1: "Text", 2: "Image", 3: "Table", 4: "Maths", 5: "Separator", 6: "Other"},  # In model`label_map`
        extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.4]  # Optional
    )
    layout = model.detect(image)
    lp.draw_box(image, layout, show_element_type=True)
    figure_blocks = lp.Layout([b for b in layout if b.type == 'Image'])
    figure_bboxes = process_blocks_to_bboxes(figure_blocks)
    return figure_bboxes
