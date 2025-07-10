#!/usr/bin/env python3
"""
DRT Multi-Agent 번역 시스템 메인 실행 파일

한국어 문장을 입력받아 multi-agent 협업을 통해 
고품질 영어 번역과 thinking trace를 생성하는 시스템입니다.
"""

import logging
import json
import os
import time
import argparse
from typing import Dict
from dotenv import load_dotenv
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed


from graph.state import State
from graph.graph_controller import DRT
from graph.visualize import visualize_and_save_graph

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경변수 로드
load_dotenv(override=True)

def run_multi_agent(drt, sentence: str) -> Dict[str, str]:
    """DRT Multi-Agent 실행"""
    initial_state = State()
    initial_state.sentence = sentence
    
    final_state = drt.graph.invoke(initial_state)
    
    return final_state 


def process_single_sentence(drt, test_sentence):
    """단일 테스트 문장을 처리합니다."""    
    result = run_multi_agent(drt, test_sentence)

    triplet = {
        "text": result['sentence'],
        "trans": result["translations"][-1],
        "thought": result["thought"]
    }

    print(triplet)

    return triplet


def process_batch(drt, sentences_batch, batch_idx):
    """문장 배치를 처리하는 함수"""
    batch_triplets = []
    
    for i, sentence in enumerate(sentences_batch):
        try:
            logger.info(sentence)
            result = run_multi_agent(drt, sentence)

            # 강제로 쉼 (API 사용량 제한 걸림)
            time.sleep(1)

            # 만약 thought 가 비어있다면 반복 횟수를 넘어서 강제 종료된 것.
            # 따라서 이 triplet 은 파일에 저장하지 않음
            if result["thought"] == "":
                logger.warning(f"배치 {batch_idx}, 문장 {i+1}: thought가 비어있어 건너뜀")
                continue
            
            triplet = {
                "text": result['sentence'],
                "trans": result["translations"][-1],
                "thought": result["thought"]
            }

            print(f"[배치 {batch_idx}] {triplet}")
            batch_triplets.append(triplet)
            
        except Exception as e:
            logger.error(f"배치 {batch_idx}, 문장 {i+1} 처리 중 오류: {e}")
            continue
    
    return batch_triplets


def process_json_file(drt, json_path, run_step):
    """JSON 파일에서 한국어 문장들을 배치 단위로 병렬 처리합니다."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        korean_sentences = []
        
        # JSON 구조 분석 및 한국어 문장 추출
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and "ko" in item:
                    korean_sentences.append(item["ko"])

        # 변수 정의
        output_file = f"data/drt_triplet_{run_step}.json"
        # 배치 크기와 동시 실행 워커 수 설정
        batch_size = 10  # 한 배치당 문장 수
        max_workers = 8   # 동시 실행할 배치 수

        start_i = batch_size * max_workers * (run_step - 1)
        end_i = batch_size * max_workers * run_step

        korean_sentences = korean_sentences[start_i:end_i]

        logger.info(f"📊 RUN_STEP: {run_step}")
        logger.info(f"📊 총 {len(korean_sentences)}개의 문장을 찾았습니다.")
        logger.info(f"🔄 배치 크기: {batch_size}, 동시 실행 워커: {max_workers}")
        
        # # 문장들을 배치로 나누기
        batches = []
        for i in range(0, len(korean_sentences), batch_size):
            batch = korean_sentences[i:i + batch_size]
            batches.append((batch, i // batch_size + 1))
        
        logger.info(f"📦 총 {len(batches)}개의 배치로 나누었습니다.")
        
        # 결과를 저장할 리스트
        all_triplets = []
        
        # 병렬 처리
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 모든 배치를 동시에 제출
            future_to_batch = {
                executor.submit(process_batch, drt, batch, batch_idx): (batch, batch_idx)
                for batch, batch_idx in batches
            }
            
            # 진행 상황 표시
            with tqdm(total=len(batches), desc="배치 처리 중") as pbar:
                for future in as_completed(future_to_batch):
                    batch, batch_idx = future_to_batch[future]
                    try:
                        batch_triplets = future.result()
                        all_triplets.extend(batch_triplets)
                        logger.info(f"✅ 배치 {batch_idx} 완료: {len(batch_triplets)}개 triplet 생성")
                        
                            
                    except Exception as e:
                        logger.error(f"❌ 배치 {batch_idx} 처리 실패: {e}")

                    finally:
                        pbar.update(1)
        
        # JSON 파일로 저장
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_triplets, f, ensure_ascii=False, indent=2)

        logger.info(f"💾 모든 번역 결과가 {output_file}에 저장되었습니다.")
        logger.info(f"📊 총 {len(all_triplets)}개의 triplet이 저장되었습니다.")
    
    
    except FileNotFoundError:
        logger.error(f"❌ 파일을 찾을 수 없습니다: {json_path}")
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON 파일 파싱 오류: {e}")
    except Exception as e:
        logger.error(f"❌ JSON 파일 처리 중 오류: {e}")


def main():
    """메인 실행 함수"""    
    # 명령행 인자 파싱
    parser = argparse.ArgumentParser(description='DRT Multi-Agent 번역 시스템')
    parser.add_argument('--run_step', type=int, default=1, 
                       help='실행할 스텝 번호 (기본값: 1)')
    
    args = parser.parse_args()
    run_step = args.run_step
    
    logger.info("🚀 DRT Multi-Agent 번역 시스템을 시작합니다.")
    logger.info(f"📊 RUN_STEP: {run_step}")
    
    # DRT 시스템 초기화
    logger.info("📊 DRT 시스템을 초기화하는 중...")
    drt = DRT()
    
    # 그래프 시각화 및 PNG 저장
    logger.info("🎨 그래프를 시각화하는 중...")
    visualize_and_save_graph(drt.graph, save_path="agent_graph.png")     

    # GOOD
    # test_sentence = "이 정도 과제는 식은 죽 먹기야."

    # BAD
    # test_sentence = "나는 남자 보는 눈이 높아요"
    # test_sentence = "나는 차은우와 화촉을 밝힌다."  
    # test_sentence = "간발의 차이로 합격이 확정됐다."

    # logger.info("📝 단일 테스트 문장으로 번역을 시작합니다.")
    # process_single_sentence(drt, test_sentence)

    logger.info("📁 JSON 파일에서 문장들을 읽어서 번역을 시작합니다.")
    kiss_json_path = "data/kiss.json"
    
    process_json_file(drt, kiss_json_path, run_step)

    
    logger.info("✨ 번역이 성공적으로 완료되었습니다!")



if __name__ == "__main__":
    main() 