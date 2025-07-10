"""
조언자 관련 프롬프트 템플릿들
"""

# 조언자 프롬프트
ADVISOR_PROMPT = """SYSTEM PROMPT:

Based on the evaluation result of the English translation of the following Korean sentence, please provide your comments and suggestions to help improve the translation.

USER PROMPT:

<Korean Sentence>
{sentence}
</Korean Sentence>
<English Translation>
{translation}
</English Translation>
<evaluation result>
{evaluation_result}
</evaluation result>
""" 