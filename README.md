# DRT: Deep Reasoning Translation via Long Chain-of-Thought
![image](https://github.com/user-attachments/assets/44a04596-41a6-46e7-86ed-54fcd6c31e0b)

## 📑 Abstract

### 목적
- 목표: LLM 이 "긴 숙고" 과정을 통해 복잡한 문장(특히 은유/직유 포함)을 더 고품질로 번역하도록 학습한다.
- 핵심 기여: 다중 에이전트 협업 프레임워크 설계 + LLM fine-tuning 데이터셋 구축

### 참고자료
- [논문](https://arxiv.org/pdf/2412.17498) / [논문 요약](https://github.com/Judy-Choi/DRT_Multi-Agent/issues/1)
- [GitHub](https://github.com/krystalan/DRT) / [HuggingFace(7B)](https://huggingface.co/Krystalan/DRT-7B)

### 전체 프로세스 개요
[[📄 실험 프로토콜] LLM 기반 긴 숙고 번역 (DRT) 학습 재현](https://github.com/Judy-Choi/DRT_Multi-Agent/issues/2)
1. 문장 수집 및 필터링
2. Multi-Agent 프레임워크 기반 DRT 데이터 생성
3. DRT 모델 학습<br>

---

## 🛠️ Setting
### Poetry 환경 설치
```shell
poetry install
```

### .env 파일 생성 & API key 세팅
```shell
touch .env

# .env
# OPENAI_API_KEY=sk-
# ANTHROPIC_API_KEY=sk-
# HF_TOKEN=hf_
```

---

## 🕸️ Multi-Agent

### Graph
![image](https://github.com/user-attachments/assets/bac1d93c-7e31-4df8-b966-904825ee51f2)

### Usage
```bash
cd multi_agent

# default
python main.py

# 각 스텝별 처리
python main.py --run_step=실행할 스텝 번호 (기본값: 1)

# 여러 스텝을 순차적으로 실행할 경우
# run_main.sh 파일에서 실행할 스텝 범위 설정 (필요에 따라 수정)
# START_STEP=1
# END_STEP=10
sh run_main.sh
```

### Dataset
초기 데이터셋으로 직접 구축한 한-영 데이터셋 [💋 KISS](https://github.com/Judy-Choi/KISS-Korean-english-Idioms-in-Sentences-dataSet) 사용
- 관용구 포함된 한국어 : 영어 번역 문장 쌍으로 구성 (7500문장)
- 초기 데이터셋 구축에 걸리는 시간 / 리소스 단축

과제 수행 시간 제한으로 인해 KISS 의 7500문장을 이용해 **DRT 학습용 데이터 총 1638 개 생성**

**DRT 학습용 데이터 예시**
- input : `<text>`
- output : `<trans>``<thought>`
```
{
  "text":"금메달의 가치가 땅에 떨어진 것입니다.",
  "trans":"The value of the gold medal has diminished.",
  "thought":"As I look at the Korean sentence, 
  I identify the keywords: \"금메달\", \"가치\", and \"땅에 떨어진\".\n
  I translate the keywords: \"금메달\" to \"gold medal\", \"가치\" to \"value, worth\", and \"땅에 떨어진\" to \"fallen to the ground\".\n
  Based on the translations of the keywords, I come up with a preliminary translation: 
  \"The value of the gold medal has fallen to the ground.\"\n
  I pause and reflect on the preliminary translation, wondering if it accurately conveys the intended meaning of the Korean sentence.\n
  I decide to iterate on the translation and try to rephrase it for better clarity and accuracy.\n
  After some thought, I revise the translation to: 
  \"The worth of the gold medal has plummeted to the ground.\"\n
  I consider the revised translation and feel more confident in its accuracy and fluency in English.\n
  I make the final decision to go with the revised translation as it captures the essence of the Korean sentence effectively."
 }
```

### Agent Framework
**LangGraph**
- 쉬운 개발 및 디버깅, 유지보수 가능 (특히 state 에 저장되는 값을 관찰하며 디버깅하기에 쉬움)
- 그래프 구조로 표현하기에 용이함 (Mermaid 시각화 참고하며 설계하기 쉽고, 노드 단위 추가/제거 쉬움)
- LangSmith 등의 모니터링 툴과 연동 (유지보수뿐만이 아니라 추후 운영 단계까지 고려)

### 특이사항
[[Docs] DRT Multi-Agent 구현 시 고려한 점](https://github.com/Judy-Choi/DRT_Multi-Agent/issues/5)
- 🔧 구현 시 고려한 점들
- 🚀 주요 개선 사항들
- ⚠️ 특이사항 및 주목할 점들


## 🧠 SFT
### Data & Train
- DRT 학습용 데이터 총 1638 개를 각각 train : valid = 1300 : 338 개로 분할해 학습
- Unsloth 를 사용해 학습 : [./sft/drt_sft_unsloth.ipynb](https://github.com/Judy-Choi/DRT_Multi-Agent/blob/main/sft/drt_sft_unsloth.ipynb)
  - Unsloth 를 사용하면 저사양에서 매우 빠르게 학습 가능 (Colab pro A100 에서 20분 내 학습 완료)
  
### Model
- Qwen2.5-7b-Instruct 모델을 Backbone 으로 사용

**학습 완료 모델 다운로드**
- [HuggingFace-File and versions-qwen25drt.Q4_K_M.gguf](https://huggingface.co/JudyChoi/qwen2.5-7b-drt/blob/main/qwen25drt.Q4_K_M.gguf)
- CLI Download:
  ```shell
  wget https://huggingface.co/JudyChoi/qwen2.5-7b-drt/resolve/main/qwen25drt.Q4_K_M.gguf -O ./sft/model/qwen25drt.Q4_K_M.gguf
  ```

**학습한 `.gguf` 모델을 Ollama 에 로드**
```bash
cd sft/model
ollama create qwen25drt -f Modelfile
# 최적화할 경우
# ollama create qwen25drt -f Modelfile_opt
ollama run qwen25drt
```

## 👷 Server
### Usage
**FastAPI uvicorn 서버 구동**
```shell
cd server
uvicorn main:app --reload
또는
uvicorn main:app --reload --log-level info
```

### 특이사항
- 번역이 잘못된 경우 지정한 횟수만큼 재번역을 수행해 번역 완성도 향상
  - `<output>...</output>` 태그가 없거나, 태그 사이에 내용이 없는 경우
  - 번역된 문장에 개행이 있는 경우 (최초 입력 문장에 개행이 없으므로)
- 재번역 결과도 잘못된 경우 최종 번역문 위치에 `[Fail Translation]` 태그로 표시해 원본과 문장 위치를 맞추고 잘못된 번역 포함 여부 / 위치를 알 수 있게 함.
- 디버깅 및 평가에 활용할 수 있도록 로그 파일 생성 (translation.log)
  - 원문 - think trace - 번역문 순서대로 로그 파일에 저장

---

## 🆚 CoT 구현 방법 및 결과 비교 : Prompt vs DRT
- 각 방법의 장점 / 단점 비교
  - [[Docs] CoT 구현 방법 비교 : Prompt vs DRT](https://github.com/Judy-Choi/DRT_Multi-Agent/issues/6)
- 번역 결과 비교
  - [[Docs] CoT 결과 비교 : Prompt vs DRT](https://github.com/Judy-Choi/DRT_Multi-Agent/issues/8)

