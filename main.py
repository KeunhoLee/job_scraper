#-*- coding:utf-8 -*-

import fire
from job_scraper import (WebDriver, 
                        KakaoJobScraper, 
                        NaverJobScraper, 
                        LineJobScraper, 
                        CoupangJobScraper, 
                        WoowahanJobScraper)
from utils.SlackMessageSender import SlackMessageSender

def scrap_jobs():
    slack_msg = SlackMessageSender()
    
    # scrap
    web_driver = WebDriver()
    
    try:
        print("kakao start")
        kakao_scraper = KakaoJobScraper(web_driver)
        kakao_scraper.scrap()
        print("kakao ok")

        print("naver start")
        naver_scraper = NaverJobScraper(web_driver)
        naver_scraper.scrap()
        print("naver ok")

        print("line start")
        line_scraper = LineJobScraper(web_driver)
        line_scraper.scrap()
        print("line ok")

        print("coupang start")
        coupang_scraper = CoupangJobScraper(web_driver)
        coupang_scraper.scrap()
        print("coupang ok")

        print("woowahan start")
        coupang_scraper = WoowahanJobScraper(web_driver)
        coupang_scraper.scrap()
        print("woowahan ok")

        slack_msg.info("Job scraping succeed")

    except Exception as e:
        raise e

    finally:    
        web_driver.close()

def scrap_job_docs():
    pass

if __name__ == "__main__":
    fire.Fire()    
