"""
번역 개선 에이전트
"""
import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from prompts.refinement_prompt import REFINEMENT_PROMPT

logger = logging.getLogger(__name__)

def create_refinement_chain(llm):
    """번역 개선 체인을 생성합니다."""
    refinement_prompt = ChatPromptTemplate.from_template(REFINEMENT_PROMPT)
    return refinement_prompt | llm | StrOutputParser()

def translator(state, refinement_chain):
    """피드백을 반영한 번역 개선을 수행합니다."""
    logger.info("Translator : Refinement translation 단계입니다.")
    sentence = state.sentence
    latest_translation = state.translations[-1]
    latest_feedback = state.feedbacks[-1] if state.feedbacks else ""

    # 키워드 참고해서 초벌번역만 했으면 바로 평가로 넘어감.
    if latest_feedback == "":
        return state 
    
    output = refinement_chain.invoke({
        "sentence": sentence, 
        "translation": latest_translation, 
        "feedback": latest_feedback,
    })
    
    logger.info(f"{output}")
    state.translations.append(output)    
    return state 
 