from OCR.paddle_ocr_func import CustomPaddle
from word.word_manager import layout_with_spaces, Document
from pdf2image import convert_from_path
from translator.gemini import GeminiTranslator
from tqdm import tqdm
import numpy as np 
import os 


def main(pdf_path, out_path, poppler_path, lang="korean"):
    ocr_obj = CustomPaddle(use_angle_cls=True, lang=lang)
    translator = GeminiTranslator(api_key=os.getenv("GOOGLE_API"))
    doc = Document()

    images = convert_from_path(pdf_path, poppler_path=poppler_path)

    for img in tqdm(images, desc="Page 변환중"):
        img = np.array(img)
        result = ocr_obj.predict_with_align(img)
        result = translator.translate(texts=result,
                             source_lang="Korean",
                             target_lang="English")
        layout_with_spaces(doc, result)
        doc.add_page_break()
    doc.save(out_path)

if __name__ == "__main__":
    pdf_path = "pdfs/full.pdf"
    out_path = "outputs/full1.docx"
    poppler_path = "C:/Users/USER/Desktop/work/python/test/2025_10_06_GPT_translate/poppler-25.07.0/Library/bin"
    main(pdf_path, out_path=out_path, poppler_path=poppler_path)