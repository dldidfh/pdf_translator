# PDF Translator

이 프로젝트는 PDF 문서를 OCR로 텍스트를 추출한 뒤 Gemini 모델을 활용해 다른 언어로 번역하고, 워드 문서 형식으로 내보내는 파이프라인을 제공합니다.

## 주요 기능
- **PaddleOCR**를 이용한 PDF 페이지 OCR 처리
- **Google Gemini** 모델을 활용한 번역 (Layout 정보를 최대한 보존)
- 번역된 결과를 **python-docx**를 통해 `.docx` 문서로 저장

## 사전 준비
1. **Python 3.10+** 환경을 권장합니다.
2. [Poppler](https://blog.alivate.com.au/poppler-windows/)를 설치하고 `bin` 디렉터리 경로를 준비합니다. `pdf2image`가 PDF를 이미지로 변환할 때 필요합니다.
3. [Google AI Studio](https://aistudio.google.com/)에서 발급받은 **Gemini API 키**를 준비합니다.

## 설치
```bash
python -m venv .venv
source .venv/bin/activate  # Windows의 경우 .venv\Scripts\activate
pip install -r requierments.txt
```

## 환경 변수 설정
Gemini API 인증을 위해 `GOOGLE_API` 환경 변수를 설정해야 합니다.

```bash
export GOOGLE_API="YOUR_GEMINI_API_KEY"  # Windows PowerShell: $Env:GOOGLE_API="..."
```

## 사용 방법
1. 번역할 PDF 파일을 준비합니다.
2. `main.py`의 예시 코드를 참고하여 경로를 설정하고 실행합니다.

```python
from main import main

pdf_path = "path/to/input.pdf"
out_path = "path/to/output.docx"
poppler_path = "path/to/poppler/bin"

main(pdf_path, out_path=out_path, poppler_path=poppler_path, lang="korean")
```

- `lang` 인자는 PaddleOCR에서 사용할 언어 모델을 지정합니다.
- 번역 결과는 기본적으로 **한국어 → 영어**로 설정되어 있으며, 필요한 경우 `translator/GeminiTranslator.translate` 호출부에서 언어를 수정할 수 있습니다.

## 디렉터리 구조
```
pdf_translator/
├── main.py                  # 전체 파이프라인 엔트리 포인트
├── OCR/
│   └── paddle_ocr_func.py   # PaddleOCR 래퍼 및 후처리 로직
├── translator/
│   ├── gemini.py            # Gemini 번역기 클래스
│   └── prompts.py           # 번역 프롬프트 구성
├── word/
│   └── word_manager.py      # 번역 결과를 Word 레이아웃으로 변환
├── requierments.txt         # Python 의존성 목록
└── README.md
```

## 주의 사항
- PaddleOCR 모델 다운로드 시 초기 실행 시간이 길어질 수 있습니다.
- Google Gemini API 호출에는 비용이 발생할 수 있으므로 쿼터를 확인하세요.
- Poppler는 시스템 경로에 따라 동작이 달라질 수 있으니, 운영체제에 맞는 설치 안내를 참고하세요.

## 라이선스
프로젝트에 라이선스가 명시되어 있지 않습니다. 필요 시 `LICENSE` 파일을 추가하여 사용 조건을 정의하세요.

