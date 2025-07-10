"""
초기 번역 에이전트
"""
import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from prompts.preliminary_prompt import PRELIMINARY_PROMPT

logger = logging.getLogger(__name__)

def create_preliminary_chain(llm):
    """초기 번역 체인을 생성합니다."""
    preliminary_prompt = ChatPromptTemplate.from_template(PRELIMINARY_PROMPT)
    return preliminary_prompt | llm | StrOutputParser()

def preliminary_translator(state, preliminary_chain):
    """초기 번역을 수행합니다."""
    logger.info("Preliminary translation 단계입니다.")
    output = preliminary_chain.invoke({
        "sentence": state.sentence,
        "keyword_translation": state.keyword_translation
    })
    
    logger.info(f"{output}")
    state.translations.append(output)
    return state 