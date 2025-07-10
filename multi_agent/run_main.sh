#!/bin/bash

# DRT Multi-Agent 시스템 순차 실행 스크립트
# 각 단계를 순차적으로 실행합니다.

echo "🚀 DRT Multi-Agent 순차 실행을 시작합니다..."

# 실행할 스텝 범위 설정 (필요에 따라 수정)
START_STEP=1
END_STEP=10

# 현재 디렉토리 확인
echo "📁 현재 작업 디렉토리: $(pwd)"
# 각 스텝을 순차적으로 실행
for step in $(seq $START_STEP $END_STEP); do
    echo ""
    echo "🔄 Step $step 실행 중..."
    echo "명령어: python main.py --run_step=$step"
    
    # main.py 실행
    python main.py --run_step=$step
    
    # 실행 결과 확인
    if [ $? -eq 0 ]; then
        echo "✅ Step $step 완료"
    else
        echo "❌ Step $step 실행 중 오류 발생"
        echo "⚠️  실행을 중단합니다."
        exit 1
    fi
    
    # 다음 스텝 전 잠시 대기 (선택사항)
    echo "⏳ 다음 스텝까지 2초 대기..."
    sleep 2
done

echo ""
echo "🎉 모든 스텝이 성공적으로 완료되었습니다!"
echo "📊 실행된 스텝: $START_STEP ~ $END_STEP"