import replicate
import os

os.environ["REPLICATE_API_TOKEN"] = "***"

output = replicate.run(
    "vaibhavs10/incredibly-fast-whisper:3ab86df6c8f54c11309d4d1f930ac292bad43ace52d10c80d87eb258b3c9f79c",
    input={
        "task": "transcribe",
        "audio": "https://replicate.delivery/pbxt/Js2Fgx9MSOCzdTnzHQLJXj7abLp3JLIG3iqdsYXV24tHIdk8/OSR_uk_000_0050_8k.wav",
        "language": "None",
        "timestamp": "chunk",
        "batch_size": 64,
        "diarise_audio": False
    }
)
print(output)
