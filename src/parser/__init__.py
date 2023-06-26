"""
Does the parsing from an image
"""
import datetime
from typing import Tuple


from paddleocr import PaddleOCR, draw_ocr
from matplotlib import pyplot as plt
import cv2
import os
import requests


def get_medication(image_path: str) -> Tuple[str, int, int, datetime.datetime, datetime.datetime]:
    """
    gets a medication from an image
    :param image_path:
    :return: tuple of prescription metadata
    """