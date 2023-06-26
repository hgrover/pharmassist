"""
Does the parsing from an image
"""
import datetime
from typing import Tuple
import re


from paddleocr import PaddleOCR, draw_ocr
from matplotlib import pyplot as plt
import cv2
import os
import requests

import openai


openai.api_key = "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"

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


def get_medication(image_path: str) -> Tuple[str, int, int, datetime.datetime, datetime.datetime]:
    """
    gets a medication from an image
    :param image_path:
    :return: tuple of prescription metadata
    """

    ocr_model = PaddleOCR(lang='en')

    result = ocr_model.ocr(image_path)

    ocr_extract = []
    for resu in result:
        for res in resu:
            ocr_extract.append(str(res[-1]))

    ocr_extract_str = '\n'.join(ocr_extract)
    prompt = f'The below is an OCR scan of a prescription label. Create a python tuple with the following information; Medication name, how many pills to take in a day (Written as "_ pills per day"), how many pills to take for each occurrence, Prescription date (numbers only), Expiration date (numbers only). Provide only the tuple, no other text. \n\n{ocr_extract_str}'
    completion = get_completion(prompt)
    rv = list(eval(completion))
    rv[-2] = datetime.datetime.strptime(rv[-2], '%m%d%Y')
    rv[-1] = datetime.datetime.strptime(rv[-1], '%m%d%Y')

    rv[1] = int(re.findall('[0-9]+', rv[1])[0])
    rv[2] = int(re.findall('[0-9]+', rv[2])[0])

    return rv



