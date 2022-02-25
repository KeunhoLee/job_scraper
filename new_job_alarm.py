#-*- coding:utf-8 -*-

import os
import requests

import pandas as pd
import fire
from utils.SlackMessageSender import SlackMessageSender

SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]

def main(*keywords):
    alarm_dict = {}

    slack_log = SlackMessageSender()

    if os.path.exists("./storage/new.csv"):
        new_jobs = pd.read_csv("./storage/new.csv")

        for idx, row in new_jobs[["job_link", "job_title", "group", "company"]].iterrows():
            row["keyword"] = []
            for keyword in keywords:
                if keyword in row.job_title.lower():
                    if row.job_link in alarm_dict.keys():
                        alarm_dict[row.job_link].keyword.append(keyword)
                    else:
                        alarm_dict[row.job_link] = row
                        alarm_dict[row.job_link].keyword.append(keyword)
        
        if alarm_dict:
            for row in alarm_dict.values():
                requests.post(SLACK_WEBHOOK_URL, json={
                                        "channel" : "#취업공고",
                                        "username": "취업공고알리미",
                                        "attachments":[
                                            {
                                                "fallback":f"새로운 관심공고 [{row.group}/{row.company}]",
                                                "text":f"[{row.group}/{row.company}] <{row.job_link}|{row.job_title}>",
                                                "color":"good",
                                                "fields":[
                                                    {
                                                    "value":f"관심 키워드 : {row.keyword}",
                                                    "short":False
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                )
        else:
            slack_log.info("새로운 관심 공고가 없습니다.")

    else:
        slack_log.info("새로운 관심 공고가 없습니다.")

if __name__ == "__main__":
    fire.Fire()