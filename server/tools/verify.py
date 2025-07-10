import re

import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_translation_result(result: str) -> bool:
    match = re.search(r'<output>(.*?)</output>', result, re.DOTALL)
    return bool(match) and '\n' not in match.group(1)


def verify_translation_quality(original_text, final_output):
    """번역 품질 검증"""
    original_lines = original_text.strip().split('\n')
    translated_lines = final_output.strip().split('\n')

    result = {
        'structure_perfect': True,
        'messages': []
    }

    # 줄 구조 검사
    if len(original_lines) != len(translated_lines):
        result['messages'].append('⚠️  줄 구조가 변경되었습니다.')
        result['structure_perfect'] = False
    else:
        result['messages'].append('✅ 줄 구조가 정확히 보존되었습니다.')

    # thinking 태그 잔존 검사
    if '<thinking>' in final_output or '</thinking>' in final_output:
        result['messages'].append('❌ 최종 결과에 thinking 태그가 남아있습니다!')
        result['structure_perfect'] = False
    else:
        result['messages'].append('✅ thinking 태그가 완전히 제거되었습니다.')

    if result['structure_perfect']:
        result['messages'].append('🎉 번역 구조가 완벽하게 보존되었습니다!')
    else:
        result['messages'].append('⚠️  구조 보존에 문제가 있습니다. 재시도를 권장합니다.')

    logger.info(result)
    return result
