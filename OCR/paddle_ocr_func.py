import logging

import numpy as np
from paddleocr import PaddleOCR


logger = logging.getLogger(__name__)

class CustomPaddle(PaddleOCR):
    def __init__(self, doc_orientation_classify_model_name=None, doc_orientation_classify_model_dir=None, doc_unwarping_model_name=None, doc_unwarping_model_dir=None, text_detection_model_name=None, text_detection_model_dir=None, textline_orientation_model_name=None, textline_orientation_model_dir=None, textline_orientation_batch_size=None, text_recognition_model_name=None, text_recognition_model_dir=None, text_recognition_batch_size=None, use_doc_orientation_classify=None, use_doc_unwarping=None, use_textline_orientation=None, text_det_limit_side_len=None, text_det_limit_type=None, text_det_thresh=None, text_det_box_thresh=None, text_det_unclip_ratio=None, text_det_input_shape=None, text_rec_score_thresh=None, return_word_box=None, text_rec_input_shape=None, lang=None, ocr_version=None, **kwargs):
        super().__init__(doc_orientation_classify_model_name, doc_orientation_classify_model_dir, doc_unwarping_model_name, doc_unwarping_model_dir, text_detection_model_name, text_detection_model_dir, textline_orientation_model_name, textline_orientation_model_dir, textline_orientation_batch_size, text_recognition_model_name, text_recognition_model_dir, text_recognition_batch_size, use_doc_orientation_classify, use_doc_unwarping, use_textline_orientation, text_det_limit_side_len, text_det_limit_type, text_det_thresh, text_det_box_thresh, text_det_unclip_ratio, text_det_input_shape, text_rec_score_thresh, return_word_box, text_rec_input_shape, lang, ocr_version, **kwargs)
    
    def predict_with_align(self, image:np.ndarray):
        logger.debug("Starting OCR prediction")
        result = self.predict(image, use_doc_orientation_classify=True)
        bboxes = result[0]["rec_boxes"]
        texts = result[0]["rec_texts"]
        grouped = self.group_text_lines(bboxes, texts)
        logger.debug("OCR prediction produced %d grouped lines", len(grouped))
        return grouped
    
    @staticmethod
    def group_text_lines(bboxes, texts, y_tolerance=25):
        """
        bboxes와 texts를 기반으로 y좌표를 기준으로 같은 줄의 텍스트를 묶고,
        줄별로 x좌표 기준으로 정렬하며, 각 줄은 통합 bbox로 반환합니다.

        :param bboxes: [(x1, y1, x2, y2), ...]
        :param texts: [text1, text2, ...]
        :param y_tolerance: 같은 줄로 간주할 y좌표 허용 오차 (픽셀 단위)
        :return: [(줄 텍스트, [min_x, min_y, max_x, max_y])] 형태의 리스트
        """
        if len(bboxes) == 0 or len(bboxes) != len(texts):
            return []

        # (y2, x1, text, bbox) 형태로 변환
        items = []
        for bbox, text in zip(bboxes, texts):
            if bbox is None or len(bbox) < 4:
                continue
            x1, y1, x2, y2 = map(float, bbox[:4])
            bottom_y = max(y1, y2)
            items.append((bottom_y, x1, text.strip(), [x1, y1, x2, y2]))

        # y2(하단 y좌표) 기준으로 정렬
        items.sort(key=lambda x: (x[0], x[1]))

        grouped_lines = []
        current_line = []
        current_y = None

        for bottom_y, x1, text, bbox in items:
            if current_y is None:
                current_y = bottom_y
                current_line = [(x1, text, bbox)]
                continue

            # 현재 라인과 y_tolerance 이내면 같은 줄로 간주
            if abs(bottom_y - current_y) <= y_tolerance:
                current_line.append((x1, text, bbox))
            else:
                # 현재 줄 정리 및 bbox 병합
                current_line.sort(key=lambda t: t[0])
                line_text = " ".join(t[1] for t in current_line)

                # bbox 합치기
                xs1 = [t[2][0] for t in current_line]
                ys1 = [t[2][1] for t in current_line]
                xs2 = [t[2][2] for t in current_line]
                ys2 = [t[2][3] for t in current_line]
                merged_bbox = [min(xs1), min(ys1), max(xs2), max(ys2)]

                grouped_lines.append((line_text, merged_bbox))

                # 새 줄 시작
                current_y = bottom_y
                current_line = [(x1, text, bbox)]

        # 마지막 줄 추가
        if current_line:
            current_line.sort(key=lambda t: t[0])
            line_text = " ".join(t[1] for t in current_line)

            xs1 = [t[2][0] for t in current_line]
            ys1 = [t[2][1] for t in current_line]
            xs2 = [t[2][2] for t in current_line]
            ys2 = [t[2][3] for t in current_line]
            merged_bbox = [min(xs1), min(ys1), max(xs2), max(ys2)]

            grouped_lines.append((line_text, merged_bbox))

        return grouped_lines
