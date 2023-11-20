import os
import logging

logging.basicConfig(filename='log/azure_proxy.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

config = {
    "api_key": os.environ.get('AZURE_OPENAI_API_KEY'),
    "proxy_src": {
        "azure": os.environ.get('AZURE_ENDPOINT')+"/openai/deployments/{}/chat/completions?api-version="+os.environ.get('AZURE_OPENAI_API_VERSION'),
        "aliyun_azure": "",
    },
    "gpt-3.5-turbo": "gpt-35-turbo",  # 模型命名
    "gpt-3.5-turbo-16k": "gpt-35-turbo-16k",
    "gpt-35-turbo": "gpt-35-turbo",
    "gpt-35-turbo-16k": "gpt-35-turbo-16k",
    "auth_key": [os.environ.get('AUTH_KEY')],
}


# logging.info(config)