from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import logging
import time
import random

from prompts.reformulator_prompts import REFORMULATION_PROMPT

logger = logging.getLogger(__name__)

def create_reformulator_chain(llm):
    """재구성 체인을 생성합니다."""
    reformulation_prompt = ChatPromptTemplate.from_template(REFORMULATION_PROMPT)
    return reformulation_prompt | llm | StrOutputParser()

def reformulator(state, reformulation_chain):
    """번역 과정을 재구성합니다."""
    logger.info("Thought Reformulation 단계입니다.")

    sentence = state.sentence

    # 키워드 번역
    keyword_text = "\n".join(f"{k}: {v}" for k, v in state.keyword_translation.items())
    parts = [keyword_text]

    # 키워드 참조한 초벌 번역
    preliminary_translation = state.translations.pop(0)
    parts.append(f"# Preliminary Translation\n{preliminary_translation}")

    # 최대 score 값 찾기
    max_score = max(eval_dict['score'] for eval_dict in state.evaluations)

    # 최대 score를 가진 모든 index 찾기
    max_indices = [i for i, eval_dict in enumerate(state.evaluations) if eval_dict['score'] == max_score]

    # 마지막 index 선택
    max_score_i = max_indices[-1]

    translations = state.translations[:max_score_i]
    feedbacks = state.feedbacks[:max_score_i]

    for (translation, feedback) in zip(translations, feedbacks):
        parts.append(f"# Translation\n{translation}")
        parts.append(f"# Feedback\n{feedback}")

    translation_process = "\n".join(parts) + "\n"  # 맨 끝 개행 추가

    output = reformulation_chain.invoke({
        "sentence": sentence,
        "translation_process": translation_process,
    })
    logger.info(f"{output}")

    sleep_time = random.uniform(0.5, 1.5)
    time.sleep(sleep_time)

    state.thought = output
    return state 