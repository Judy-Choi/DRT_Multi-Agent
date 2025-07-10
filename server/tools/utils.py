import os

def save_to_file(path, text):
    """결과를 파일에 저장"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)

def load_default_text(NOVEL_PATH):
    """기본 텍스트 파일을 로드합니다."""
    if os.path.exists(NOVEL_PATH):
        with open(NOVEL_PATH, encoding='utf-8') as f:
            return f.read()
    return "번역할 한국어 문장을 입력해 주세요."