#-*- coding:utf-8 -*-

import os
import requests
from datetime import datetime

SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]

class SlackMessageSender:

    def __init__(self, channel=None, username=None, icon_url=None):
        self.channel = channel
        self.username = username
        self.icon_url = icon_url

    def _timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _print_n_send(self, payload):
        print(payload["text"])
        requests.post(SLACK_WEBHOOK_URL, json=payload)

    def send_message(self, text, tag=None):
        text = f"|\t{tag}\t| " + text if tag else text
        text_to_send = f"[ {self._timestamp()} ] " + text
        
        payload = {
            "text" : text_to_send,
            "channel" : self.channel,
            "username" : self.username,
            "icon_url" : self.icon_url
            }

        self._print_n_send(payload)

    def debug(self, text):
        self.send_message(text, tag="DEBUG")

    def info(self, text):
        self.send_message(text, tag="INFO")

    def warning(self, text):
        self.send_message(text, tag="WARNING")

    def error(self, text):
        self.send_message(text, tag="ERROR")


if __name__ == "__main__":
    test = SlackMessageSender()
    test.send_message("테스트메시지입니다.", "TEST")
    test.info("테스트 INFO")
    test.error("에러발생!")