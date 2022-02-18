#-*- coding:utf-8 -*-

import os
import pandas as pd
import fire
from utils.SlackMessageSender import SlackMessageSender

def main(*keywords):
    alarm_dict = {}

    slack_log = SlackMessageSender()
    slack_direct_msg = SlackMessageSender(channel="#취업공고",
                                          username="취업공고알리미")


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
                slack_direct_msg.info(
                    f"새로운 관심공고 [{row.group}/{row.company}] {row.job_title} : {row.keyword}"
                    )
        else:
            slack_log.info("새로운 관심 공고가 없습니다.")

    else:
        slack_log.info("새로운 관심 공고가 없습니다.")

if __name__ == "__main__":
    fire.Fire()