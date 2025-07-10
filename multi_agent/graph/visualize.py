"""
그래프 시각화 함수들
"""

def visualize_and_save_graph(graph, save_path=None):
    """
    그래프를 시각화하고 선택적으로 PNG 파일로 저장합니다.
    
    Args:
        graph: LangGraph 객체
        save_path (str, optional): PNG 파일로 저장할 경로
    """
    try:
        # 먼저 그래프 구조를 텍스트로 출력
        print("📊 그래프 구조:")
        print(f"노드: {list(graph.nodes.keys())}")
        
        # Mermaid 다이어그램 생성 시도
        try:
            mermaid_code = graph.get_graph().draw_mermaid()
            print("📋 Mermaid 다이어그램:")
            print(mermaid_code)
        except Exception as e:
            print(f"⚠️ Mermaid 다이어그램 생성 실패: {e}")
        
        # PNG 생성 시도
        try:
            png_data = graph.get_graph().draw_mermaid_png()
            
            # PNG 파일로 저장
            if save_path:
                with open(save_path, 'wb') as f:
                    f.write(png_data)
                print(f"✅ 그래프가 {save_path}에 저장되었습니다.")
        except Exception as e:
            print(f"⚠️ PNG 생성 실패: {e}")
            print("텍스트 다이어그램으로 대체합니다.")
        
        # Jupyter 환경에서 시각화
        try:
            from IPython.display import Image, display
            if 'png_data' in locals():
                display(Image(png_data))
        except ImportError:
            print("Jupyter 환경이 아니므로 시각화를 건너뜁니다.")
            
    except Exception as e:
        print(f"❌ 그래프 시각화 전체 실패: {e}")
        import traceback
        traceback.print_exc() 