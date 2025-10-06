from OCR.paddle_ocr_func import CustomPaddle
from word.word_manager import WordManager
from pdf2image import convert_from_path
from tqdm import tqdm
import numpy as np 


def main(pdf_path, out_path, poppler_path, lang="korean"):
    ocr_obj = CustomPaddle(use_angle_cls=True, lang=lang)
    doc = WordManager(out_path)

    images = convert_from_path(pdf_path, poppler_path=poppler_path)

    for img in tqdm(images, desc="Page 변환중"):
        img = np.array(img)
        result = ocr_obj.predict_with_align(img)

        for res in result:
            doc.add_para(res)
        
    doc.save()

if __name__ == "__main__":
    pdf_path = "pdfs/하장풍력발전 업무위탁계약서_240924(날인O).pdf"
    out_path = "outputs/하장풍력1.docx"
    poppler_path = "C:/Users/USER/Desktop/work/python/test/2025_10_06_GPT_translate/poppler-25.07.0/Library/bin"
    main(pdf_path, out_path=out_path, poppler_path=poppler_path)