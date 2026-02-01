import sys
import os

# ✅ Ensure project root is in Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

import gradio as gr

from image.image_input import image_input
from image.image_pipeline import process_image


def run_pipeline(image):
    """
    Runs full image-only pipeline:
    - verification
    - classification
    - urgency
    """
    return process_image(image)


gr.Interface(
    fn=run_pipeline,
    inputs=image_input,
    outputs="json",
    title="Nagrik Sahayak – Image Only Civic Issue Detection",
    description="Upload an image of pothole, garbage, or street light to analyze the issue."
).launch(share=True)


