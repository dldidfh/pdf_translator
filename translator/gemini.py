import ast
import logging
import time

import google.generativeai as genai

from translator.prompts import get_prompt


logger = logging.getLogger(__name__)


class GeminiTranslator:
    """
    Gemini API를 사용하여 텍스트를 번역하는 클래스.
    """
    def __init__(self, api_key: str):
        """
        클래스 초기화 시 API 키를 설정하고 모델을 불러옵니다.

        Args:
            api_key (str): Google AI Studio에서 발급받은 API 키.
        """
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("Gemini model successfully initialized")
        except Exception as e:
            logger.exception("Model initialization failed: %s", e)
            self.model = None

    
    def translate(self, texts, source_lang: str = "Korean", target_lang: str = "English",
                  max_retries: int = 3, retry_delay: float = 2.0):
        """
        입력된 텍스트를 지정된 언어로 번역합니다. 실패 시 자동 재시도합니다.

        Args:
            texts: 번역할 OCR 텍스트 리스트
            source_lang (str): 원본 언어
            target_lang (str): 대상 언어
            max_retries (int): 재시도 횟수 (기본 3)
            retry_delay (float): 재시도 간 대기 시간(초) (기본 2.0초)

        Returns:
            list[tuple[str, tuple[int,int,int,int]]] | str: 
            번역 결과 리스트 또는 실패 시 빈 문자열
        """
        if not self.model:
            logger.error("Gemini model is not initialized. Check API key.")
            return ""

        prompt = get_prompt(texts, source_lang=source_lang, target_lang=target_lang)

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(
                    "Starting translation attempt %d/%d for %d text items",
                    attempt,
                    max_retries,
                    len(texts) if hasattr(texts, "__len__") else 0,
                )
                response = self.model.generate_content(prompt)
                if not response or not getattr(response, "text", None):
                    raise ValueError("Empty response or missing text field.")

                parsed = parse_llm_output(response.text.strip())
                logger.info("Translation succeeded on attempt %d", attempt)
                return parsed

            except Exception as e:
                logger.warning(
                    "Translation attempt %d/%d failed: %s", attempt, max_retries, e, exc_info=True
                )
                if attempt < max_retries:
                    time.sleep(retry_delay)
                else:
                    logger.error("Maximum retry attempts exceeded. Returning empty string.")
                    return ""


def parse_llm_output(output_str):
    """
    LLM이 문자열로 반환한 리스트 형태
    예: '[("Text", (x1,y1,x2,y2)), ("Text2", (x1,y1,x2,y2))]'
    를 실제 Python 객체로 안전하게 변환
    """
    try:
        data = ast.literal_eval(output_str)
    except Exception as e:
        logger.exception("Failed to parse LLM output: %s", e)
        raise ValueError(f"Failed to parse LLM output: {e}")

    # 안전성 검사
    parsed = []
    for item in data:
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            continue
        text, bbox = item
        if not isinstance(text, str):
            continue
        if not isinstance(bbox, (tuple, list)) or len(bbox) != 4:
            continue
        bbox = tuple(map(int, bbox))
        parsed.append((text, bbox))
    logger.debug("Parsed LLM output into %d items", len(parsed))
    return parsed
