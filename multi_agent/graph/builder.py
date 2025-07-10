"""
번역 그래프 빌더 모듈
"""
from langgraph.graph import END, StateGraph
import logging

logger = logging.getLogger(__name__)

def build_translation_graph(State, node_functions, control_edge_func):
    """
    번역을 위한 LangGraph를 구성합니다.
    
    Args:
        State: 상태 클래스
        node_functions: 노드 함수들의 딕셔너리
        control_edge_func: 조건부 엣지 함수
        threshold: 평가 임계값
    
    Returns:
        컴파일된 그래프 객체
    """
    graph = StateGraph(State)

    # 노드 추가
    for node_name, node_func in node_functions.items():
        graph.add_node(node_name, node_func)

    # 시작점 설정
    graph.set_entry_point("word_level_translator")

    # 초기 preprocessing 단계
    graph.add_edge("word_level_translator", "preliminary_translator")
    graph.add_edge("preliminary_translator", "translator")

    # 순환 단계
    graph.add_edge("translator", "evaluator")

    graph.add_conditional_edges(
        "evaluator", 
        control_edge_func, 
        {
            "CONTINUE": "advisor",
            "DONE": "reformulator"
        }
    )

    graph.add_edge("advisor", "translator")

    # reformulator 종료
    graph.add_edge("reformulator", END)

    return graph.compile() 