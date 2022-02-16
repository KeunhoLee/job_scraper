#-*- coding:utf-8 -*-

import fire
from job_scraper import (JobScraper,
                        WebDriver, 
                        KakaoJobScraper, 
                        NaverJobScraper, 
                        LineJobScraper, 
                        CoupangJobScraper, 
                        WoowahanJobScraper)
from utils.SlackMessageSender import SlackMessageSender

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

def scrap_job_texts():
    ''' '''
    pass

if __name__ == "__main__":
    fire.Fire()    
