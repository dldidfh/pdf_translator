def join_ocr_texts_with_bbox(ocr_results, sep=" "):
    """
    OCR 결과 [(text, [x1,y1,x2,y2]), ...] 형태를
    'text(x1,y1,x2,y2)' 식으로 묶어 한 문장으로 반환.
    """
    if not ocr_results:
        return ""

    parts = []
    for item in ocr_results:
        if not isinstance(item, (tuple, list)) or len(item) < 2:
            continue

        text, bbox = item[0], item[1]
        if not text or not isinstance(bbox, (list, tuple)) or len(bbox) < 4:
            continue

        # 안전하게 숫자만 추출
        x1, y1, x2, y2 = map(int, bbox[:4])
        parts.append(f"{text}({x1},{y1},{x2},{y2})")

    return sep.join(parts).strip()


def get_prompt(texts, source_lang, target_lang, merge_px_min=30):
    str_text = join_ocr_texts_with_bbox(texts)
    return f"""
You are an expert document translator specialized in OCR-based layout preservation.

Below is OCR-extracted text with its bounding box coordinates.
Each element follows this format:  text(x1,y1,x2,y2)
The coordinates indicate each text’s position on the page.

Your task:
1. Translate all text from **{source_lang}** into **{target_lang}**.
2. Maintain the **exact output format** below (Python list of tuples):
3. Output only the translated list — no comments, explanations, or extra text.

Input OCR data:
{str_text}

Output only the translated list in the format described above.
"""

