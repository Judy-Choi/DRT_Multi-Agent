"""
키워드 번역 프롬프트
"""

WORD_LEVEL_PROMPT = """SYSTEM PROMPT:
Given an Korean sentence, identify the important words (usually nouns, verbs, technical terms, idioms, and named entities that require special attention in translation) and translate them into English.
Output the translation in JSON format, for example:

{{"KoreanWord1": "EnglishTranslation", "KoreanWord2": "EnglishTranslation"}}

The English translations can be a single translation or multiple options as deemed appropriate.

USER PROMPT:

<Korean Sentence>
{sentence}
</Korean Sentence>
""" 