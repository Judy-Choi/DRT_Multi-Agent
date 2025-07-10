from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import logging

from prompts.advisor_prompts import ADVISOR_PROMPT

logger = logging.getLogger(__name__)

def create_advisor_chain(llm):
    """조언자 체인을 생성합니다."""
    advisor_prompt = ChatPromptTemplate.from_template(ADVISOR_PROMPT)
    return advisor_prompt | llm | StrOutputParser()

def advisor(state, advisor_chain):
    """번역에 대한 피드백을 제공합니다."""
    logger.info("Advisor 피드백 단계입니다.")
    latest_translation = state.translations[-1]
    reason = state.evaluations[-1]["reason"]
    output = advisor_chain.invoke({
        "sentence": state.sentence,
        "translation": latest_translation,
        "evaluation_result": reason,
    })
    
    logger.info(f"{output}")
    state.feedbacks.append(output)    
    return state 