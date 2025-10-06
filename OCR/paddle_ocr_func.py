from paddleocr import PaddleOCR
import numpy as np 

class CustomPaddle(PaddleOCR):
    def __init__(self, doc_orientation_classify_model_name=None, doc_orientation_classify_model_dir=None, doc_unwarping_model_name=None, doc_unwarping_model_dir=None, text_detection_model_name=None, text_detection_model_dir=None, textline_orientation_model_name=None, textline_orientation_model_dir=None, textline_orientation_batch_size=None, text_recognition_model_name=None, text_recognition_model_dir=None, text_recognition_batch_size=None, use_doc_orientation_classify=None, use_doc_unwarping=None, use_textline_orientation=None, text_det_limit_side_len=None, text_det_limit_type=None, text_det_thresh=None, text_det_box_thresh=None, text_det_unclip_ratio=None, text_det_input_shape=None, text_rec_score_thresh=None, return_word_box=None, text_rec_input_shape=None, lang=None, ocr_version=None, **kwargs):
        super().__init__(doc_orientation_classify_model_name, doc_orientation_classify_model_dir, doc_unwarping_model_name, doc_unwarping_model_dir, text_detection_model_name, text_detection_model_dir, textline_orientation_model_name, textline_orientation_model_dir, textline_orientation_batch_size, text_recognition_model_name, text_recognition_model_dir, text_recognition_batch_size, use_doc_orientation_classify, use_doc_unwarping, use_textline_orientation, text_det_limit_side_len, text_det_limit_type, text_det_thresh, text_det_box_thresh, text_det_unclip_ratio, text_det_input_shape, text_rec_score_thresh, return_word_box, text_rec_input_shape, lang, ocr_version, **kwargs)
    
    def predict_with_align(self, image:np.ndarray):
        result = self.predict(image, use_doc_orientation_classify=True)
        bboxes = result[0]["rec_boxes"]
        texts = result[0]["rec_texts"]
        return self.group_text_lines(bboxes, texts)

    @staticmethod
    def group_text_lines(ocr_result, y_tolerance=10):
        """
        OCR 결과를 y좌표 기준으로 그룹화하여 문단 리스트를 반환합니다.
        
        :param ocr_result: PaddleOCR의 결과 리스트 (e.g., result[0])
        :param y_tolerance: 같은 줄로 판단할 y좌표의 최대 허용 오차 (픽셀 단위)
        :return: 그룹화된 문단 텍스트의 리스트
        """
        if not ocr_result:
            return []

        # 텍스트 블록을 y좌표(세로), x좌표(가로) 순으로 정렬합니다.
        # box[0][1]은 좌측 상단 y좌표, box[0][0]은 좌측 상단 x좌표입니다.
        ocr_result.sort(key=lambda x: (x[0][0][1], x[0][0][0]))

        paragraphs = []
        current_line_texts = []
        # 첫 번째 줄의 평균 y좌표를 기준으로 시작합니다.
        last_avg_y = (ocr_result[0][0][0][1] + ocr_result[0][0][3][1]) / 2

        for res in ocr_result:
            box, (text, _) = res
            top_left_y, bottom_left_y = box[0][1], box[3][1]
            current_avg_y = (top_left_y + bottom_left_y) / 2

            # 이전 줄과의 y좌표 차이가 허용 오차 이내이면 같은 줄(문단)로 간주합니다.
            if abs(current_avg_y - last_avg_y) <= y_tolerance:
                current_line_texts.append(text)
            else:
                # y좌표 차이가 크면, 새로운 문단이 시작된 것으로 판단합니다.
                # 지금까지 묶인 텍스트들을 하나의 문단으로 합치고 리스트에 추가합니다.
                if current_line_texts:
                    paragraphs.append(" ".join(current_line_texts))
                # 새로운 문단을 현재 텍스트로 시작합니다.
                current_line_texts = [text]
            
            last_avg_y = current_avg_y

        # 마지막으로 처리된 문단을 추가합니다.
        if current_line_texts:
            paragraphs.append(" ".join(current_line_texts))

        return paragraphs