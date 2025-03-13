#!/bin/bash

echo 'export TF_VAR_OPENAI_ENC_KEY="${encoder_key}"' >> ~/.bashrc
echo 'export TF_VAR_OPENAI_API_KEY_NAME="${keyname}"' >> ~/.bashrc
source ~/.bashrc

sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip -y
sudo apt install python3-venv -y
sudo apt install nginx -y

# SSL certifcate generation
sudo apt install certbot -y
sudo apt install python3-certbot-nginx -y

# python virtual environment
cd /home/ubuntu
python3 -m venv gradio_env
source gradio_env/bin/activate
pip install gradio openai dotenv tiktoken boto3 cryptography