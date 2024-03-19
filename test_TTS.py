import replicate
import os

os.environ["REPLICATE_API_TOKEN"] = "***"

# # cjwbw/seamless_communication
# output = replicate.run(
#     "cjwbw/seamless_communication:668a4fec05a887143e5fe8d45df25ec4c794dd43169b9a11562309b2d45873b0",
#     input={
#         "task_name": "T2ST (Text to Speech translation)",
#         "input_text": "說個笑話，不好笑要重新講",
#         "input_text_language": "Mandarin Chinese",
#         "max_input_audio_length": 60,
#         "target_language_text_only" : "Mandarin Chinese",
#         "target_language_with_speech": "Mandarin Chinese"
#     }
# )
# print(output)


# suno-ai/bark  #跑不出東西
output = replicate.run(
    "suno-ai/bark:b76242b40d67c76ab6742e987628a2a9ac019e11d56ab96c4e91ce03b79b2787",
    input={
        "prompt": "說個笑話，不好笑要重新講 ",
        "text_temp": 0.7,
        "output_full": False,
        "waveform_temp": 0.7,
        "history_prompt": "announcer"
    }
)
print(output)

# Hello, my name is Suno. And, uh — and I like pizza.
# 說個笑話，不好笑要重新講 
