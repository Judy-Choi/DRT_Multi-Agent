"""
키워드 번역 에이전트
"""
import json
import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from prompts.word_level_prompt import WORD_LEVEL_PROMPT

logger = logging.getLogger(__name__)

def create_word_level_chain(llm):
    """키워드 번역 체인을 생성합니다."""
    word_level_prompt = ChatPromptTemplate.from_template(WORD_LEVEL_PROMPT)
    return word_level_prompt | llm | StrOutputParser()

def word_level_translator(state, word_level_chain):
    """키워드 번역을 수행합니다."""
    logger.info("Word-level translation 단계입니다.")
    output = word_level_chain.invoke({"sentence": state.sentence})
    logger.info(f"{output}")
    
    try:
        state.keyword_translation = json.loads(output)
    except json.JSONDecodeError:
        state.keyword_translation = {"error": "JSON 파싱 실패", "raw": output}

    return state 