import google.generativeai as genai
from translator.prompts import get_prompt
import ast


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
            print("✅ Gemini 모델이 성공적으로 초기화되었습니다.")
        except Exception as e:
            print(f"🚨 모델 초기화 중 오류 발생: {e}")
            self.model = None

    def translate(self, texts, source_lang: str = "Korean", target_lang: str = "English") -> str:
        """
        입력된 텍스트를 지정된 언어로 번역합니다.

        Args:
            text (str): 번역할 텍스트.
            source_lang (str): 원본 텍스트의 언어.
            target_lang (str): 번역할 대상 언어.

        Returns:
            str: 번역된 텍스트. 번역 실패 시 빈 문자열을 반환합니다.
        """
        if not self.model:
            return "모델이 초기화되지 않았습니다. API 키를 확인하세요."

        # 번역 작업을 명확하게 지시하는 프롬프트 구성
        prompt = get_prompt(texts, source_lang=source_lang, target_lang=target_lang)

        try:
            response = self.model.generate_content(prompt)
            # 번역된 텍스트에서 불필요한 공백 제거 후 반환
            return parse_llm_output(response.text.strip()) if response.text else "번역 결과를 가져올 수 없습니다."
        except Exception as e:
            return f"번역 중 오류가 발생했습니다: {e}"


def parse_llm_output(output_str):
    """
    LLM이 문자열로 반환한 리스트 형태
    예: '[("Text", (x1,y1,x2,y2)), ("Text2", (x1,y1,x2,y2))]'
    를 실제 Python 객체로 안전하게 변환
    """
    try:
        data = ast.literal_eval(output_str)
    except Exception as e:
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
    return parsed
