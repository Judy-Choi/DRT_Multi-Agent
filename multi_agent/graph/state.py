"""
번역 시스템의 상태 클래스 정의
"""
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class State:
    sentence: str = ""   # 입력 문장
    keyword_translation: Dict[str, str] = field(default_factory=dict) # 키워드 직역

    # Multi-Agent 3총사
    translations: List[str] = field(default_factory=list) # 번역 결과
    feedbacks: List[str] = field(default_factory=list) # Advisor 피드백
    evaluations: List[Dict[str, str]] = field(default_factory=list) # Evaluator 피드백

    # Agent 반복
    iteration: int = 0 # 반복 횟수
    
    # 번역 종료 후 번역 과정 고찰
    thought: str = "" 