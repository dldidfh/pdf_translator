import logging
import os
from pathlib import Path

import numpy as np
from pdf2image import convert_from_path
from tqdm import tqdm

from OCR.paddle_ocr_func import CustomPaddle
from translator.gemini import GeminiTranslator
from word.word_manager import Document, layout_with_spaces


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main(pdf_path, out_path, poppler_path, lang="korean"):
    pdf_path = Path(pdf_path)
    poppler_path = Path(poppler_path) if poppler_path else None
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    ocr_output_path = out_path.with_name(f"{out_path.stem}_ocr{out_path.suffix}")
    images_output_dir = out_path.parent / pdf_path.stem
    images_output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Starting PDF translation process for %s -> %s", pdf_path, out_path)

    ocr_obj = CustomPaddle(use_angle_cls=True, lang=lang)
    translator = GeminiTranslator(api_key=os.getenv("GOOGLE_API"))
    translated_doc = Document()
    ocr_doc = Document()

    try:
        images = convert_from_path(
            str(pdf_path), poppler_path=str(poppler_path) if poppler_path else None
        )
        logger.info("Converted PDF to %d images", len(images))
    except Exception as exc:
        logger.exception("Failed to convert PDF to images: %s", exc)
        raise

    for index, image in enumerate(tqdm(images, desc="Page 변환중"), start=1):
        logger.info("Processing page %d", index)
        image_path = images_output_dir / f"page_{index:03d}.png"
        try:
            image.save(image_path)
            logger.info("Saved page image to %s", image_path)
        except Exception:
            logger.exception("Failed to save image for page %d", index)

        np_image = np.array(image)
        try:
            ocr_result = ocr_obj.predict_with_align(np_image)
            logger.info("OCR completed for page %d with %d entries", index, len(ocr_result))
        except Exception:
            logger.exception("OCR failed for page %d", index)
            continue

        layout_with_spaces(ocr_doc, ocr_result)
        ocr_doc.add_page_break()

        try:
            translated_result = translator.translate(
                texts=ocr_result, source_lang="Korean", target_lang="English"
            )
        except Exception:
            logger.exception("Translation raised an unexpected exception on page %d", index)
            continue

        if translated_result == "":
            logger.error("Translation failed for page %d; skipping page", index)
            continue

        layout_with_spaces(translated_doc, translated_result)
        translated_doc.add_page_break()

    translated_doc.save(out_path)
    logger.info("Saved translated document to %s", out_path)

    ocr_doc.save(ocr_output_path)
    logger.info("Saved OCR document to %s", ocr_output_path)


if __name__ == "__main__":
    pdf_path = "pdfs/full.pdf"
    out_path = "outputs/full1.docx"
    poppler_path = "C:/Users/USER/Desktop/work/python/test/2025_10_06_GPT_translate/poppler-25.07.0/Library/bin"
    main(pdf_path, out_path=out_path, poppler_path=poppler_path)
