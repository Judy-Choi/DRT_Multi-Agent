"""
번역 관리자 클래스
"""
from typing import Dict
import logging
import json
import os
from datetime import datetime

from .state import State
from config.loader import create_llm, MAX_ITERATIONS
from agents.word_level_translator import word_level_translator, create_word_level_chain
from agents.preliminary_translator import preliminary_translator, create_preliminary_chain
from agents.refinement_translator import translator, create_refinement_chain
from agents.evaluator import create_evaluator_chain, evaluator
from agents.advisor import create_advisor_chain, advisor
from agents.reformulator import create_reformulator_chain, reformulator
from .builder import build_translation_graph

logger = logging.getLogger(__name__)

class DRT:
    def __init__(self):
        """DRT 시스템 초기화"""
        # LLM 초기화
        self.llm = create_llm()
        
        # 체인들 생성
        self.word_level_chain = create_word_level_chain(self.llm)
        self.preliminary_chain = create_preliminary_chain(self.llm)
        self.refinement_chain = create_refinement_chain(self.llm)
        self.evaluator_chain = create_evaluator_chain(self.llm)
        self.advisor_chain = create_advisor_chain(self.llm)
        self.reformulation_chain = create_reformulator_chain(self.llm)
        
        # 그래프 구성
        node_functions = {
            "word_level_translator": self._word_level_translator_node,
            "preliminary_translator": self._preliminary_translator_node,
            "translator": self._translator_node,
            "evaluator": self._evaluator_node,
            "advisor": self._advisor_node,
            "reformulator": self._reformulator_node
        }
        
        self.graph = build_translation_graph(
            State=State,
            node_functions=node_functions,
            control_edge_func=self._control_edge,
        )

    def _control_edge(self, state: State):
        """평가 결과에 따른 조건부 라우팅"""
        logger.info(f"조건부 엣지 호출: iteration={state.iteration}, MAX_ITERATIONS={MAX_ITERATIONS}")
        
        # 반복 횟수가 최대치에 도달했는지 확인
        if state.iteration >= MAX_ITERATIONS:
            logger.info("DONE : 반복 횟수 임계값 초과")
            return "DONE"
        elif len(state.evaluations) > 1 and state.evaluations[-1]['score'] == state.evaluations[-2]['score']:
            logger.info("DONE : 점수 변화 없음")
            return "DONE"
        else:
            logger.info("CONTINUE : Advisor 에게 Feedback 을 받습니다")
            return "CONTINUE"

    # 노드 래퍼 함수들
    def _word_level_translator_node(self, state: State) -> State:
        return word_level_translator(state, self.word_level_chain)
    
    def _preliminary_translator_node(self, state: State) -> State:
        return preliminary_translator(state, self.preliminary_chain)
    
    def _translator_node(self, state: State) -> State:
        return translator(state, self.refinement_chain)
    
    def _evaluator_node(self, state: State) -> State:
        return evaluator(state, self.evaluator_chain)
    
    def _advisor_node(self, state: State) -> State:
        return advisor(state, self.advisor_chain)
    
    def _reformulator_node(self, state: State) -> State:
        return reformulator(state, self.reformulation_chain)
