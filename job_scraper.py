#-*- coding:utf-8 -*-

import os
import re
import time
import datetime
import numpy as np
import pandas as pd

from abc import *

from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

CHROME_DRIVER_PATH = os.environ["CHROME_DRIVER_PATH"]

class WebDriver:
    def __init__(self):
        self.is_driver_on = False
        self.set_driver()

    def set_driver(self):
        if not self.is_driver_on:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--headless")
            webdriver_service = Service(CHROME_DRIVER_PATH)
            self.driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

            self.is_driver_on = True
        else:
            raise Exception("available driver already exist.")

    def browse(self, url): 
        self.driver.get(url)

    def rand_sleep(self, sec=1):
        time.sleep(np.random.exponential(sec))

    def fixed_sleep(self, sec=1):
        time.sleep(sec)

    def implicitly_wait(self, sec=1):
        self.driver.implicitly_wait(sec)

    def get_page_src(self):
        return self.driver.page_source

    def close(self):
        self.driver.close()
        self.is_driver_on = False

class JobScraper(metaclass=ABCMeta):

    def __init__(self, driver, group_name):
        self.driver = driver
        self.group_name = group_name

        self.timestamp = datetime.datetime.now()
        self.job_df = pd.DataFrame()
        self.file_path = f"./storage/{group_name}/"
        self.file_name = group_name + f"_{self.timestamp.strftime('%Y%m%d%H%M%S')}.csv"

    @abstractmethod
    def _init_for_scrap(self):
        pass
    
    @abstractmethod
    def _scrap_job_info(self):
        pass
    
    @abstractmethod
    def _format_job_info(self): #TODO: 형식 통일하여 공통 메서드 만들기
        pass

    def _insert_attrs(self):
        self.job_df["group"] = self.group_name
        self.job_df["timestamp"] = self.timestamp.strftime('%Y-%m-%d %H:%M:%S')

    def _save_result(self):

        if not os.path.exists(self.file_path):
            os.makedirs(self.file_path)
            
        self.job_df.to_csv(self.file_path + self.file_name, index=False)

    def scrap(self):
        self._init_for_scrap()
        self._scrap_job_info()
        self._format_job_info()
        self._insert_attrs()
        self._save_result()

    def get_job_df(self):
        return self.job_df

class KakaoJobScraper(JobScraper):

    def __init__(self, driver):
        super().__init__(driver, "kakao")
        self.base_url = "https://careers.kakao.com"
        self.job_cond = "/jobs?company=ALL&part=TECHNOLOGY"
        self.max_page = 0
        self.result = []

    def _init_for_scrap(self):
        
        self.driver.browse(self.base_url + self.job_cond)
        self.driver.implicitly_wait(1)
        
        html = self.driver.get_page_src()
        soup = BeautifulSoup(html, 'html.parser')
        page_number = soup.find('a', {"class": "change_page btn_lst"})

        max_page = re.search("page=(.+?)$", page_number["href"]).group(1)
        self.max_page = int(max_page)

    def _scrap_job_info(self):

        for pn in range(1, self.max_page+1):
            
            page_url = self.base_url + self.job_cond + "&page=" + str(pn)

            self.driver.browse(page_url)
            html = self.driver.get_page_src()
            soup = BeautifulSoup(html, 'html.parser')

            area_info_list = soup.findAll("div", {"class": "area_info"})

            job_info = []
            for area_info in area_info_list:
                main_info = area_info.find("a", {"class":"link_jobs"})
                if main_info is None:
                    continue

                job_link = main_info["href"]
                job_title = main_info.find("h4", {"class":"tit_jobs"}).text

                sub_titles = area_info.findAll("dt")
                sub_contents = area_info.findAll("dd")

                sub_info_dict = {sub_title.text:sub_content.text for sub_title, sub_content in zip(sub_titles, sub_contents)}

                skill_set_tag = []
                for tag in area_info.findAll("a", {"class":"link_tag"}):
                    skill_set_tag.append(tag["data-code"])

                job_info.append((job_link, job_title, sub_info_dict, skill_set_tag))
            
            self.driver.rand_sleep(3)

            self.result.extend(job_info)

    def _format_job_info(self):

        job_df = pd.DataFrame()
        for r in self.result:
            
            tmp = {"job_link":self.base_url + r[0], 
                   "job_title":r[1],
                   "skill_set_tag":[r[3]]}
            tmp = {**tmp, **r[2]}

            job_df = pd.concat([job_df, pd.DataFrame(tmp, columns=tmp.keys())], axis=0)

        job_df = job_df.rename(columns={"영입마감일":"deadline",
                                        "회사정보":"company"})

        job_df = job_df[["company", "job_title", "job_link", "skill_set_tag", "deadline"]]

        self.job_df = job_df.reset_index(drop=True)

class NaverJobScraper(JobScraper):

    def __init__(self, driver):
        super().__init__(driver, "naver")
        self.base_url = "https://recruit.navercorp.com"
        self.job_cond = "/naver/job/list/developer"
        self.result = []

    def _init_for_scrap(self):
        
        self.driver.browse(self.base_url + self.job_cond)
        self.driver.implicitly_wait(1)

        is_more_page = True
        i = 1
        while is_more_page: 
            try:
                btn = self.driver.driver.find_element(By.CLASS_NAME, 'more_btn')
                btn.click()
                print(f"Click {i}")
                i += 1
                self.driver.fixed_sleep(2)
            except Exception as e:
                print("Bottom.")
                is_more_page = False

    def _scrap_job_info(self):

        html = self.driver.get_page_src()
        soup = BeautifulSoup(html, 'html.parser')
        card_list = soup.find('div', {"class": "card_list"}).findAll("li")

        company_dict = {"sml_NB_ci":"Naver_Cloud",
                "sml_NFN_ci":"NAVER_FINANCIAL",
                "sml_NL_ci":"NAVER_LABS",
                "sml_SN_ci":"SNOW",
                "sml_WM_ci":"WORKS_MOBILE",
                "sml_WTKR_ci":"Naver_Webtoon",
                "sml_KR_ci":"NAVER"}

        for card in card_list:

            company_img = card.find("img")["src"]
            company = re.match("\/img\/common\/(.*?).png", company_img).group(1)
            job_link = card.a["href"]
            job_title = card.strong.get_text()
            
            deadline = card.em.get_text()
            skill_set_tag = []
            for tag in card.find("span", {"class":"tag_area"}).findAll("a"):
                skill_set_tag.append(tag.get_text())

            self.result.append((company_dict.get(company, company), job_link, job_title, deadline, skill_set_tag))

    def _format_job_info(self):

        job_df = pd.DataFrame()

        for r in self.result:
            
            tmp = {"company":r[0],
                   "job_link":self.base_url + r[1], 
                   "job_title":r[2],
                   "deadline":r[3],
                   "skill_set_tag":[r[4]]}

            job_df = pd.concat([job_df, pd.DataFrame(tmp, columns=tmp.keys())], axis=0)

        job_df = job_df[["company", "job_title", "job_link", "skill_set_tag", "deadline"]]

        self.job_df = job_df.reset_index(drop=True)

class LineJobScraper(JobScraper):

    def __init__(self, driver):
        super().__init__(driver, "line")
        self.base_url = "https://careers.linecorp.com"
        self.job_cond = "/ko/jobs?ca=All"
        self.result = []

    def _init_for_scrap(self):
        self.driver.browse(self.base_url + self.job_cond)
        self.driver.implicitly_wait(5)

    def _scrap_job_info(self):

        html = self.driver.get_page_src()
        soup = BeautifulSoup(html, 'html.parser')
        job_list = soup.find('ul', {"class": "job_list"}).findAll("li")

        for job in job_list:

            sub_tags = job.find("div", {"class":"text_filter"}).findAll("span")
            
            if len(sub_tags):
                company = sub_tags[1].get_text()
                skill_set_tag = [sub_tags[2].get_text()]
            else:
                company = ""
                skill_set_tag = [] 

            job_link = job.a["href"]
            job_title = job.find("h3", {"class":"title"}).get_text()
            
            deadline = job.find("span", {"class":"date"}).get_text()

            self.result.append((company, job_link, job_title, deadline, skill_set_tag))

    def _format_job_info(self):

        job_df = pd.DataFrame()

        for r in self.result:
            
            tmp = {"company":r[0],
                "job_link":self.base_url + r[1], 
                "job_title":r[2],
                "deadline":r[3],
                "skill_set_tag":[r[4]]}

            job_df = pd.concat([job_df, pd.DataFrame(tmp, columns=tmp.keys())], axis=0)

        job_df = job_df[["company", "job_title", "job_link", "skill_set_tag", "deadline"]]

        self.job_df = job_df.reset_index(drop=True)

class CoupangJobScraper(JobScraper):

    def __init__(self, driver):
        super().__init__(driver, "coupang")
        self.base_url = "https://www.coupang.jobs"
        self.job_cond = "/kr/jobs/?page=1#results"
        self.max_page = 0
        self.result = []

    def _init_for_scrap(self):
        self.driver.browse(self.base_url + self.job_cond)
        self.driver.implicitly_wait(2)

        html = self.driver.get_page_src()
        soup = BeautifulSoup(html, 'html.parser')
        page_number = soup.find('a', {"rel":"last"})

        max_page = page_number.get_text()
        self.max_page = int(max_page)

    def _scrap_job_info(self):
        job_items = []

        current_page = 1

        while current_page <= self.max_page:
            html = self.driver.get_page_src()
            soup = BeautifulSoup(html, "html.parser")
            job_items.extend(soup.findAll("a", {"class":"stretched-link"}))

            self.driver.fixed_sleep(1)
            self.driver.browse(self.base_url + f"/kr/jobs/?page={str(current_page+1)}#results")
            self.driver.fixed_sleep(1)

            current_page += 1

        for job in job_items:
            
            company = "coupang"
            deadline = np.nan
            skill_set_tag = []

            job_link = job["href"]
            job_title = job.get_text()

            self.result.append((company, job_link, job_title, deadline, skill_set_tag))
            
    def _format_job_info(self):

        job_df = pd.DataFrame()

        for r in self.result:
            
            tmp = {"company":r[0],
                "job_link":self.base_url + r[1], 
                "job_title":r[2],
                "deadline":r[3],
                "skill_set_tag":[r[4]]}

            job_df = pd.concat([job_df, pd.DataFrame(tmp, columns=tmp.keys())], axis=0)

        job_df = job_df[["company", "job_title", "job_link", "skill_set_tag", "deadline"]]

        self.job_df = job_df.reset_index(drop=True)