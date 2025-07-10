from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
import logging

from prompts.evaluator_prompts import EVALUATOR_PROMPT

logger = logging.getLogger(__name__)

def create_evaluator_chain(llm):
    """평가 체인을 생성합니다."""
    evaluator_prompt = ChatPromptTemplate.from_template(EVALUATOR_PROMPT)
    return evaluator_prompt | llm | StrOutputParser()

def evaluator(state, evaluator_chain):
    """번역을 평가합니다."""
    logger.info("Evaluator 평가 단계입니다.")
    latest_translation = state.translations[-1]
    score_text = evaluator_chain.invoke({
        "sentence": state.sentence,
        "translation": latest_translation
    })

    try:
        score_dict = json.loads(score_text)
    except json.JSONDecodeError:
        score_dict = {"error": "JSON 파싱 실패", "raw": score_text}

    state.evaluations.append(score_dict)

    # Score 파싱
    score = int(score_dict.get("score", 0)) if isinstance(score_dict, dict) and "score" in score_dict else 0
    reason = score_dict.get("reason", "") if isinstance(score_dict, dict) else ""

    logger.info(f"평가 결과: Score={score}, Reason={reason}")

    state.iteration += 1
    return state 