#-*- coding:utf-8 -*-

from job_scraper import WebDriver, KakaoJobScraper, NaverJobScraper, LineJobScraper, CoupangJobScraper

if __name__ == "__main__":
    
    # scrap
    web_driver = WebDriver()
    
    try:
        # kakao_scraper = KakaoJobScraper(web_driver)
        # kakao_scraper.scrap()
        # print("kakao ok")

        # naver_scraper = NaverJobScraper(web_driver)
        # naver_scraper.scrap()
        # print("naver ok")

        # line_scraper = LineJobScraper(web_driver)
        # line_scraper.scrap()
        # print("line ok")

        coupang_scraper = CoupangJobScraper(web_driver)
        coupang_scraper.scrap()
        print("coupang ok")

    except Exception as e:
        raise e

    finally:    
        web_driver.close()
