from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from tqdm import tqdm
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.chat_models import ChatOllama
from tools.utils import load_default_text, save_to_file
from tools.verify import verify_translation_result, verify_translation_quality

import logging
import os
import re

# --- 기본 설정 ---
# .env 파일에서 환경변수 불러오기
load_dotenv(override=True)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI()

# --- 경로 및 상수, 기본값 정의 ---
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')
NOVEL_PATH = os.path.join(DATA_DIR, 'novel.txt')
INPUT_PATH = os.path.join(DATA_DIR, 'input.txt')
RAW_OUTPUT_PATH = os.path.join(DATA_DIR, 'translation.log')
CLEAN_OUTPUT_PATH = os.path.join(DATA_DIR, 'translated.txt')

# 번역 실패 시 재시도 횟수
MAX_RETRY_COUNT = 3


# --- 모델 초기화 ---
# 모델 이름은 ollama에 설치된 모델 명과 일치해야 함
try:
    translate_drt_ollama = ChatOllama(model="qwen25drt:latest", streaming=False)
    logger.info("Ollama 모델 로딩 성공: qwen25drt:latest")
except Exception as e:
    logger.error(f"Ollama 모델 로딩 실패: {e}")
    translate_drt_ollama = None


# # Request 모델 정의
class TranslateRequest(BaseModel):
    text: str = load_default_text(NOVEL_PATH)

@app.post("/translate")
async def translate(req: TranslateRequest):
    """번역 함수"""
    text = req.text.strip()

    # 입력받은 원문 저장
    save_to_file(INPUT_PATH, text)

    logger.info("입력받은 텍스트를 문장 단위로 분할하고 번역을 시작합니다.")
    text_prepared = text.split('\n')
    raw_translated_texts = []
    translated_texts = []

    for i, source_text in tqdm(enumerate(text_prepared)):
        logger.info(f"번역 중... {i+1}/{len(text_prepared)}")

        raw_translated_texts.append(source_text)

        if source_text == "":
            translated_texts.append("[NEWLINE]")
            raw_translated_texts.append("[NEWLINE]")
            continue

        result = translate_drt_ollama.invoke([
            SystemMessage(content="You are a philosopher skilled in deep thinking, accustomed to exploring complex problems with profound insight."),
            HumanMessage(content=f"Please translate the following text from Korean to English:\n{source_text}")
        ]).content.strip()

        is_translation_valid = verify_translation_result(result)

        # 번역이 잘 되었으면 로그와 번역 결과 각각 저장하고 다음 문장 번역
        if is_translation_valid:
            raw_translated_texts.append(result)
            match = re.search(r'<output>(.*?)</output>', result, re.DOTALL)
            extracted_text = match.group(1).strip()
            translated_texts.append(extracted_text)
            continue

        else:
            retry_count = 1
            while(retry_count <= MAX_RETRY_COUNT):
                logger.info(f"번역 재시도 : {retry_count}/{MAX_RETRY_COUNT}")

                result = translate_drt_ollama.invoke([
                    SystemMessage(content="You are a philosopher skilled in deep thinking, accustomed to exploring complex problems with profound insight."),
                    HumanMessage(content=f"Please translate the following text from Korean to English:\n{source_text}")
                ]).content.strip()

                is_translation_valid = verify_translation_result(result)

                # 번역이 잘 되었으면 로그와 번역 결과 각각 저장하고 while 문 탈출
                if is_translation_valid:
                    raw_translated_texts.append(result)
                    match = re.search(r'<output>(.*?)</output>', result, re.DOTALL)
                    extracted_text = match.group(1).strip()
                    translated_texts.append(extracted_text)
                    break

                retry_count += 1

            if retry_count > MAX_RETRY_COUNT:
                # 재시도 횟수 초과 시 번역 실패 처리
                raw_translated_texts.append(result)
                translated_texts.append("[Failed Translation]")

    cleaned_texts = [text.replace('[NEWLINE]', '') for text in translated_texts]
    cleaned_texts = '\n'.join(cleaned_texts)

    raw_translated_texts= '\n'.join(raw_translated_texts)

    save_to_file(RAW_OUTPUT_PATH, raw_translated_texts)
    save_to_file(CLEAN_OUTPUT_PATH, cleaned_texts)

    # 번역 품질 검사
    quality_result = verify_translation_quality(text, cleaned_texts)

    return {"translated": cleaned_texts, "quality_check": quality_result}
