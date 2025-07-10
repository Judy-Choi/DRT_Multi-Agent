"""
초기 번역 프롬프트
"""

PRELIMINARY_PROMPT = """SYSTEM PROMPT:

Given a Korean sentence and a JSON object containing potential translations of important keywords, refer to the JSON object and produce an English literal translation of the entire sentence. 

Please output **only** the English translation of the sentence — do **not** include any explanations, comments, or formatting.  
Your response must be **plain English text only**, with **no JSON, no bullet points, no markdown, no headings, and no surrounding phrases**.

USER PROMPT:

<Korean Sentence>
{sentence}
</Korean Sentence>
<Potential Keyword Translation>
{keyword_translation}
</Potential Keyword Translation>""" 