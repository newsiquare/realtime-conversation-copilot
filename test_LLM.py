import replicate
import os

os.environ["REPLICATE_API_TOKEN"] = "***"

_transcript  = "說個笑話"
_prompt_text = "您是一位專業的語言治療師，擅長提供故事、笑話等方式，吸引兒童並改善語言治療。簡短，少於150字。" 


_prompt = f"""
{_transcript}
------
{_prompt_text}
"""

print('get-suggestion/_prompt = ', _prompt)

_suggestion = ""
for event in replicate.stream(
    "mistralai/mistral-7b-instruct-v0.2",
    input={
        "debug": False,
        "top_k": 50,
        "top_p": 0.9,
        "prompt": _prompt,
        "temperature": 0.6,
        "max_new_tokens": 512,
        "min_new_tokens": -1,
        "prompt_template": "<s>[INST] {prompt} [/INST] ",
        "repetition_penalty": 1.15,
    },
):
    _suggestion += str(event)  # Accumulate the output

print ('suggestion = ', _suggestion)
