"""
재구성 관련 프롬프트 템플릿들
"""

# 재구성 프롬프트
REFORMULATION_PROMPT = """A student is engaged in the task of translating a Korean sentence into English. 

The Korean sentence is as follows: 
<Korean Sentence>
{sentence}
</Korean Sentence> 

This student constantly thinks about and optimizes their translation. The whole process is shown as follows: 

<Translation Process>
{translation_process}
</Translation Process> 

Please polish the whole translation process into a long first-person self-reflection description (use the present tense). 

The self-reflection should begin with selecting the keywords from the Korean sentence, translating the keywords, then attempting to translate the whole sentence, thinking about whether the translation is good or not, and iteratively making translation attempts. Finally, make a final translation decision. 

Output the self-reflection description directly without any additional descriptions or explanations. Each line in the self-reflection description can be regarded as a reasoning step toward the translation.

""" 