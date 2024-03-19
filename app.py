from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_from_directory
from flask_cors import CORS, cross_origin
import flask_restful as restful
import replicate
import os
import boto3
import logging
import tempfile
from multiprocessing.pool import ThreadPool
from faster_whisper import WhisperModel
from werkzeug.utils import secure_filename
import ollama

# ollama
ollamaModel = 'gemma:7b'


# AWS S3 Bucket
aws_access_key = "AKIA5XHZCLWGNTVJKVZR"
aws_secret_key = "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"
bucket_name = "conversationcopliot"
s3 = boto3.client("s3", aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)

# Replicate, REPLICATE_API_TOKEN environment variable
os.environ["REPLICATE_API_TOKEN"] = "r8_D8MWaMlttrIvVpwkDcI4JBhzFqKlv1x2OnZNu"


UPLOAD_FOLDER_AUDIO = './temp_audio'
ALLOWED_EXTENSIONS_AUDIO = set(['mp3'])

app = Flask(__name__)
api = restful.Api(app)
modelReplicate = replicate

app.config['UPLOAD_FOLDER_AUDIO'] = UPLOAD_FOLDER_AUDIO


# render html
@app.route("/")
def index():
    return render_template("index.html")


@app.route('/hello', methods=['GET'])
def home():
    return "<h1>Hello, I am here !</h1>"


# ---------------------------------------------------------------------------------
#
# Restful API
#
# ---------------------------------------------------------------------------------
# API測試資料
testPath = "/test"
testJSON = [{'id': 1, 'title': 'cute'},{'id': 2, 'title': 'happy'}]

# API接口
@app.route('/api/v1%s' %testPath , methods=['GET'])
def get_tasks():
    return jsonify({'test': testJSON})


# ---------------------------------------------------------------------------------
#
#  Faster Whisper
#
# ---------------------------------------------------------------------------------
# 音檔語言
lang = "自動判斷"                             # @param ["自動判斷", "en", "zh", "ja", "fr", "de"]

#VAD filter
vad_filter = True                            # @param {type:"boolean"}
vad_filter_min_silence_duration_ms = 50      # @param {type:"integer"}

# 提示語(想輸出繁體中文可用)
initial_prompt = "以下是繁體中文的句子"         # @param ["", "以下是繁體中文的句子", "以下是简体中文的句子"]

# Word-level timestamps(以字為單位切時間)
word_level_timestamps = False                # @param {type:"boolean"}

# "GPU" or "CPU"
# device = "cuda"
device = "cpu"                               # compute_type = "int8" , 使用cpu時compute_type改用int8
compute_type = "int8"                        # @param {type:"string"} ['float16', 'int8_float16', 'int8']

# 選擇模型
modelType = "large-v3"                       # @param ["medium", "large-v1", "large-v2", "large-v3"]

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS_AUDIO

@app.route("/process-audio-whisper", methods=["POST"])
def faster_whisper_ai_start():

    # 單檔
    file = request.files['audio']
    audio_data = file.read()
    print('type(file) = ', type(file))
    print('type(audio_data) = ', type(audio_data))
    file.stream.seek(0)
    if file :
        filename = "test01.mp3"                    # random, fileName = time.time() + '.mp3'
        # filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER_AUDIO'], filename))

    # # 多檔
    # flist = request.files.getlist("file[]")
    # for f in flist:
    #     fileName = time.time() + '.mp3'
    #     file.save(os.path.join(app.config['UPLOAD_FOLDER_AUDIO'], filename))

    print("transcribe audio...")
    try:
        # with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        #     temp_audio.write(audio_data)
        #     temp_audio.flush()
        # audioFilename = temp_audio.name   
        
        print(f'-------準備開始辨識 and Flush----------',flush=True)
        audioFilename = os.path.join(app.config['UPLOAD_FOLDER_AUDIO'], filename)
        print('audioFilename = ', audioFilename)
        
        model = WhisperModel(modelType, device=device, compute_type=compute_type)
        segments, info = model.transcribe(audioFilename, beam_size=5,
                                        language=None if lang == "自動判斷" else lang,
                                        initial_prompt=None if initial_prompt == "" else initial_prompt,
                                        word_timestamps=word_level_timestamps,
                                        vad_filter=vad_filter,
                                        vad_parameters=dict(min_silence_duration_ms=vad_filter_min_silence_duration_ms))

        print ('initial_prompt = ', initial_prompt)
        print(f'偵測到的語言 "{info.language}" 可能性 {info.language_probability}',flush=True)
        
        #results 轉好的文字陣列
        results= []
        for segment in segments:
            if word_level_timestamps:
                for word in segment.words:
                    segment_dict = {'start':word.start,'end':word.end,'transcript':word.word}
                    results.append(segment_dict)
                    # results = segment_dict 
        else:
            segment_dict = {'start':segment.start,'end':segment.end,'transcript':segment.text}
            results.append(segment_dict)
            # results = segment_dict
        
        print('results = ', results)
        print('results[-1][transcript] = ', results[-1]['transcript'])
        return jsonify(results[-1])
    except RuntimeError as e:
        print(f'{e}',flush=True)
        print(f'-------error----------',flush=True)
        return 'error'
    except:
        return 'error'
    

# ---------------------------------------------------------------------------------
#
#  ollama
#
# ---------------------------------------------------------------------------------
@app.route('/chat', methods=['GET', 'POST'])
@cross_origin()
def chat():
    print("Getting Chat...")
    data        = request.get_json()  # Parse JSON data from the request
    query       = data.get("transcript", "")  # Extract transcript
    prompt_text = data.get("prompt", "")  # Extract prompt text
    # query       = '說個笑話'

    print('chat/transcript = ', query)
    print('chat/prompt_text = ', prompt_text)
    
    prompt = f"""
    {query}
    ------
    {prompt_text}
    """

    # query = request.args.get('query') if request.method == 'GET' else request.form.get('query')
    if query is not None:
        ss = ollama.generate(model=ollamaModel, prompt=prompt)
        print('ss[\'response\'] = ', ss['response'])
        return jsonify({"suggestion": ss['response']})
    else:
        return jsonify({"error": "query field is missing"}), 400


# ---------------------------------------------------------------------------------
#
#  Remote API - Replicate 語音辨識
#
# ---------------------------------------------------------------------------------
# use Replicate - transcript audio using whisper
@app.route("/process-audio", methods=["POST"])
def process_audio_data():
    audio_data = request.files["audio"].read()

    print("Processing audio...")
    # Create a temporary file to save the audio data
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            temp_audio.write(audio_data)
            temp_audio.flush()

            s3.upload_file(temp_audio.name, bucket_name, temp_audio.name)
            temp_audio_uri = f"https://{bucket_name}.s3.amazonaws.com/{temp_audio.name}"

        output = modelReplicate.run(
            "vaibhavs10/incredibly-fast-whisper:3ab86df6c8f54c11309d4d1f930ac292bad43ace52d10c80d87eb258b3c9f79c",
            input={
                "task": "transcribe",
                "audio": temp_audio_uri,
                "language": "english",
                "timestamp": "chunk",
                "batch_size": 64,
                "diarise_audio": False,
            },
        )

        print(output)
        results = output["text"]

        return jsonify({"transcript": results})
    except Exception as e:
        print(f"Error running Replicate model: {e}")

    print("Processing audio End...")
    return None


# ---------------------------------------------------------------------------------
#
#  Remote API - Replicate LLM回覆
#
# ---------------------------------------------------------------------------------
# use Replicate - generate suggestion using mixtral
@app.route("/get-suggestion", methods=["POST"])
def get_suggestion():
    print("Getting suggestion...")
    _data        = request.get_json()  # Parse JSON data from the request
    _transcript  = _data.get("transcript", "")  # Extract transcript
    _prompt_text = _data.get("prompt", "")  # Extract prompt text
    # _transcript  = "說個笑話"
    # _prompt_text = "您是一位專業的語言治療師，擅長提供故事、笑話等方式，吸引兒童並改善語言治療。簡短，少於150字。" 

    print('get-suggestion/_transcript = ', _transcript)
    print('get-suggestion/_prompt_text = ', _prompt_text)

    _prompt = f"""
    {_transcript}
    ------
    {_prompt_text}
    """

    print('get-suggestion/_prompt = ', _prompt)

    _suggestion = ""
    for event in modelReplicate.stream(
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
    return jsonify({"suggestion": _suggestion})  # Send as JSON response



# =======================================================
# 測試上傳
# =======================================================
# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# @app.route('/postpic', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         file = request.files['file']
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             return redirect(url_for('uploaded_file', filename=filename))
#     return '''
#         <!doctype html>
#         <title>Upload new File</title>
#         <h1>Upload new File</h1>
#         <form action="" method=post enctype=multipart/form-data>
#         <p><input type=file name=file>
#             <input type=submit value=Upload>
#         </form> 
#     '''

# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == "__main__":
    app.run()
