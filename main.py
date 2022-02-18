#-*- coding:utf-8 -*-

import os
import datetime

import pandas as pd
import fire
from job_scraper import (JobScraper,
                        WebDriver, 
                        KakaoJobScraper, 
                        NaverJobScraper, 
                        LineJobScraper, 
                        CoupangJobScraper, 
                        WoowahanJobScraper)
from utils.SlackMessageSender import SlackMessageSender

DATA_HOME = "./storage"

def scrap_job_list():
    ''' '''
    slack_msg = SlackMessageSender()
    failures = []

    # scrap
    web_driver = WebDriver()
    
    try:
        print("kakao start")
        kakao_scraper = KakaoJobScraper(web_driver)
        kakao_scraper.scrap()
        print("kakao ok")
    except Exception as e:
        failures.append("kakao")
        slack_msg.err(f"Kakao job failed with : {e}") 

    try:
        print("naver start")
        naver_scraper = NaverJobScraper(web_driver)
        naver_scraper.scrap()
        print("naver ok")
    except Exception as e:
        failures.append("naver")
        slack_msg.err(f"Naver job failed with : {e}") 
    
    try:
        print("line start")
        line_scraper = LineJobScraper(web_driver)
        line_scraper.scrap()
        print("line ok")
    except Exception as e:
        failures.append("line")
        slack_msg.err(f"Line job failed with : {e}") 

    try:
        print("coupang start")
        coupang_scraper = CoupangJobScraper(web_driver)
        coupang_scraper.scrap()
        print("coupang ok")
    except Exception as e:
        failures.append("coupang")
        slack_msg.err(f"Coupang job failed with : {e}") 

    try:
        print("woowahan start")
        coupang_scraper = WoowahanJobScraper(web_driver)
        coupang_scraper.scrap()
        print("woowahan ok")
    except Exception as e:
        failures.append("woowahan")
        slack_msg.err(f"Woowahan job failed with : {e}")

    web_driver.close()
    
    if not failures:
        slack_msg.info("Job scraping succeed")
    elif len(failures) == JobScraper.num_companies:
        slack_msg.error("All jobs failed")
    else:
        slack_msg.warning(f"Some jobs failed : {failures}")

def merge_data():
    ''' '''
    slack_msg = SlackMessageSender()
    job_file_name = os.path.join(DATA_HOME, "merged_jobs.csv")

    def _load_all_data(data_path=DATA_HOME):
        
        company_list = [dir for dir in os.listdir(data_path) if ".csv" not in dir]

        jobs_df = pd.DataFrame()

        for company in company_list:
            file_list = os.listdir(os.path.join(data_path, company))
            
            for file in file_list:
                jobs_df = pd.concat([jobs_df, pd.read_csv(os.path.join(data_path, company, file))], axis=0)

        return jobs_df.reset_index(drop=True)

    def _load_recent_data(data_path=DATA_HOME):
        company_list = [dir for dir in os.listdir(data_path) if ".csv" not in dir]

        jobs_df = pd.DataFrame()

        for company in company_list:
            file_list = os.listdir(os.path.join(data_path, company))
            file_list = sorted(file_list, reverse=True)
            jobs_df = pd.concat([jobs_df, pd.read_csv(os.path.join(data_path, company, file_list[0]))], axis=0)

        return jobs_df.reset_index(drop=True)

    try:

        if os.path.isfile(job_file_name):
            old = pd.read_csv(job_file_name)
            jobs_df = _load_recent_data()
            
            # old에 없던 data를 new로 따로 저장
            new_jobs = [job for job in jobs_df.job_link if job not in old.job_link.to_list()]
            new = jobs_df[jobs_df.job_link.isin(new_jobs)]

            merged = pd.concat([old, new], axis=0)
            merged = merged.sort_values(
                by=['company', 'job_title', 'job_link', 'deadline', 'group', 'timestamp']
            )
            merged = merged.drop_duplicates(['company', 'job_title', 'job_link', 'deadline', 'group'], keep="first")
            merged["last_updated"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            new.to_csv(os.path.join(DATA_HOME, "new.csv"), index=False)
            merged.to_csv(job_file_name, index=False)
        else:
            jobs_df = _load_all_data()
            jobs_df = jobs_df.sort_values(
                by=['company', 'job_title', 'job_link', 'deadline', 'group', 'timestamp']
            )
            jobs_df = jobs_df.drop_duplicates(['company', 'job_title', 'job_link', 'deadline', 'group'], keep="first")
            jobs_df["last_updated"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            jobs_df.to_csv(job_file_name, index=False)

    except Exception as e:
        slack_msg.err(f"Merging data failed with : {e}")
        raise e

def scrap_job_texts():
    ''' '''
    pass

if __name__ == "__main__":
    fire.Fire()
