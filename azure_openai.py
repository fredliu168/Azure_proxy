# coding:utf-8
import requests
import json
import flask
from flask import Flask, request
from src.config import config
from src.SSEClient import SSEClient

app = Flask(__name__)


@app.route("/v1/chat/completions", methods=["POST"])
def chat_process():
    data = request.get_data()
    json_data = json.loads(data.decode("utf8"))
    auth_header = request.headers.get("Authorization")
    Proxy_src = request.headers.get("Proxy_src")
    if auth_header is None:
        return "Unauthorized", 401
        
    auth_token = auth_header.split(" ")[1]

    if auth_token not in config["auth_key"]:
        return "Unauthorized", 401

    use_stream = json_data["stream"]
    reqHeaders = {
            "content-type": "application/json",
            "api-key": config["api_key"],
        }

    model = json_data["model"]

    if Proxy_src is None or Proxy_src not in config["proxy_src"]:  # 判断访问路径
        reqUrl = config["proxy_src"]["azure"].format(config[model])
    else:
        reqUrl = config["proxy_src"][Proxy_src].format(config[model])

    def stream(json_data):        
        resp = requests.post(reqUrl, stream=True, headers=reqHeaders, json=json_data)
        client = SSEClient(resp)
        for event in client.events():
            yield ("data: " + event.data + "\n\n")

    if use_stream:
        return flask.Response(stream(json_data), mimetype="text/event-stream")
    else:
        resp = requests.post(reqUrl, headers=reqHeaders, json=json_data)
        return flask.Response(resp.content, mimetype="application/json")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8090)
