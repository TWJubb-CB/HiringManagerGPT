import os
import datetime
import functools
import logging
import pathlib

import gradio as gr
import openai
import tiktoken
import dotenv
import boto3
from logger import logger
from logging.handlers import RotatingFileHandler

from encryption import decrypt_api_key
logging.getLogger('boto3').setLevel(logging.INFO)
logging.getLogger('botocore').setLevel(logging.INFO)
logging.getLogger('gradio').setLevel(logging.INFO)
logging.getLogger('openai').setLevel(logging.INFO)
logging.getLogger('tiktoken').setLevel(logging.INFO)
dotenv.load_dotenv()

# whether running HTTPS locally (for testing)
USE_HTTPS = False
LOCAL_API_KEY = True

def setup_log(logger):

    LOG_DIR = os.path.join(str(pathlib.Path().absolute()), "logs")
    if not os.path.exists(LOG_DIR):
        print("Creating Log Dir : {}".format(LOG_DIR))
        os.mkdir(LOG_DIR)
    else:
        print("Using Log Dir : {}".format(LOG_DIR))

    now = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    log_fpath = os.path.join(LOG_DIR, fr"prompt_logs_{now}.log")
    log_file_handler = RotatingFileHandler(log_fpath, maxBytes=10000000, backupCount=50)
    log_file_handler.setFormatter(
        logging.Formatter('%(asctime)s %(levelname)s %(lineno)d:%(filename)s - %(message)s'))
    log_file_handler.setLevel(logging.INFO)

    logger.addHandler(log_file_handler)

    logger.info(f"Logging to file {log_fpath}")
    return logger

logger = setup_log(logger)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(console_handler)

force_dark_mode = """
function refresh() {
    const url = new URL(window.location);
    if (url.searchParams.get('__theme') !== 'dark') {
        url.searchParams.set('__theme', 'dark');
        window.location.href = url.href;
    }
}
"""

def get_api_key(name: str, region:str="eu-west-2"):
    dotenv.load_dotenv()
    logger.info(f"Loading SSM Parameter {name} from aws")
    # ensure there is an encryption key
    OPENAI_ENC_KEY = os.getenv('TF_VAR_OPENAI_ENC_KEY')
    logger.info(OPENAI_ENC_KEY)

    ssm = boto3.client("ssm", region_name=region)
    response = ssm.get_parameter(Name=name, WithDecryption=True)
    api_key_encrypted = response["Parameter"]["Value"]

    return decrypt_api_key(api_key_encrypted,
                           enc_key=OPENAI_ENC_KEY)

if LOCAL_API_KEY:
    api_key = os.getenv("TF_VAR_OPENAI_API_KEY")
else:
    api_key = get_api_key(name=os.getenv('TF_VAR_OPENAI_API_KEY_NAME'),
                          region="eu-west-2")

client = openai.OpenAI(api_key=api_key)

with open(os.path.join(str(pathlib.Path(__file__).absolute().parent), "data/system_prompt.txt"), "r") as f:
    system_prompt = f.read()

with open(os.path.join(str(pathlib.Path(__file__).absolute().parent), "data/cv.txt"), "r") as f:
    user_prompt_prefix = f.read()


def stream_gpt(prompt, logger):

    if len(prompt) == 0:
        return ""


    logger.info(fr"Prompt: {prompt}")

    enc = tiktoken.encoding_for_model("gpt-4o-mini")
    tokens = len(enc.encode(user_prompt_prefix + prompt))
    cost = tokens / 1e6 * 5
    logger.info(fr"Estimated Cost : ${cost:.2f} ({tokens} tokens)")

    if tokens > 10000 or cost > 0.10:
        logger.info("Cannot complete query, too expensive!")
        return "Cannot complete query, too expensive!"

    messages= [
        {"role": "system",
         "content": """You are an assistant responsible for filtering questions to decide if they are appropriate. 
        - Questions should be professional in nature.
        - Questions relating to Tom's experience now or in the past are ok.
        - Asking for contact details is Ok
        You must respond in the format "Yes" or "No", followed by an explanation of why you have answered Yes or No. 
        """},
        {"role": "user", "content": "A client has asked the following question : \n" + prompt + "\n Is this an appropriate question?"}
      ]
    check = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=messages,
        stream=False
    )
    check = check.choices[0].message.content

    if check.startswith("Yes"):
        logger.info(check)
    else:
        logger.info("Question does not meet required standard:")
        logger.info(check)
        yield check[3:]
        return

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_prefix + "\n" + prompt}
      ]
    stream = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=messages,
        stream=True
    )
    result = ""
    for chunk in stream:
        result += chunk.choices[0].delta.content or ""
        yield result
        if not chunk.choices[0].delta.content:
            logger.info(result)


logger.info(fr"Creating interface")
demo = gr.Interface(fn=functools.partial(stream_gpt, logger=logger),
                    clear_btn=None,
                    submit_btn="Ask",
                    allow_flagging="never",
                    inputs=[gr.Textbox(label="Ask a question about Tom's experience", lines=2)],
                    outputs=[gr.Markdown(label="Response:")],
                    theme = gr.themes.Default(primary_hue="purple",
                                              secondary_hue="purple",
                                              neutral_hue="gray",
                                              font=gr.themes.GoogleFont("Lato", weights=(100, 300)),
                                              # font_mono=gr.themes.GoogleFont("IBM Plex Mono", weights=(100, 300))
                                              ),
                    css="footer{display:none !important}"
                    )

if USE_HTTPS:
    demo.launch(server_name="0.0.0.0",
                server_port=7860,
                ssl_verify=False,
                ssl_keyfile="./ssl/local/key.pem",
                ssl_certfile="./ssl/local/cert.pem")
else:
    demo.launch(server_name="0.0.0.0",
                server_port=7860)
