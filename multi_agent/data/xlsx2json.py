import pandas as pd
import json

# 경로는 사용자의 예시 기준에 맞춰서 설정
xlsx_file_path = "KISS.xlsx"
json_file_path = "kiss.json"

# 헤더 없이 불러오기
df = pd.read_excel(xlsx_file_path, header=None)

# 필요한 두 번째와 세 번째 컬럼만 선택해서 dict로 변환
data = [{"ko": row[1], "en": row[2]} for row in df.itertuples(index=False)]

# JSON 파일로 저장
with open(json_file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)