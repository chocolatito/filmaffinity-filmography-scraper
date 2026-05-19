from logging import Logger
import random
import re
import time

from src import constants
from src.parser_mixin import ParserMixin
from src import utils


class Crawler(ParserMixin):

    PARAMS = {
        'stext': '',
        'stype[]': 'title',
        'country': '',
        'genre': '',
        'fromyear': '',
        'toyear': '',
    }
    BASE_URL = "https://www.filmaffinity.com/us"
    SEARCH_URL = f"{BASE_URL}/advsearch.php"
    FILMOGRAPHY_URL = (BASE_URL+"/name-movies.php?name-id=%s"
                       "&role-cat=none&orderby=date-desc&v=slist&p=1")
    XPATH_DICT = {
        "director": ('//h1[@id="main-title"]/following-sibling::div//ul/li'
                     '//div[contains(@class,"director")]//span/a[@title]'),
        "title_links": '//main[@id="mt-content-cell"]//div/ul/li//ul/li/div/a',
        "ancestor_year": "ancestor::ul[1]/preceding-sibling::div[1]",
        "href_links": '//nav/ul/li/a[contains(@href, "&p=")]/@href',
    }

    def __init__(self, base_logger: Logger) -> None:
        self.logger = utils.adapter_log(base_logger, {"worker_id": "CRAWLER"})
        self.title_result = []
        if constants.PROXY is None:
            self.proxies = {}
        else:
            self.proxies = {"http": constants.PROXY, "https": constants.PROXY}
        self.configure_parser(proxies=self.proxies)
        self.results_by_title = []
        self.director_dict = {}

    def processe_single_page(self,
                             url: str,
                             check_total_pages: bool = False) -> list | tuple[int, list]:
        self.logger.info(f"Fetching page {url}")
        tree = self.get_tree(url)
        result_list = []
        href_list = tree.xpath(self.XPATH_DICT["title_links"])
        for href in href_list:
            result = {}
            result["title"] = href.attrib["title"]
            result["url"] = href.attrib["href"]
            result["data_movie_id"] = re.search(r"/film(\d+).html", result["url"]).group(1)
            result["year"] = href.xpath(self.XPATH_DICT["ancestor_year"])[0].text_content()
            result_list.append(result)
        if check_total_pages is False:
            return result_list
        self.logger.info("Obtaining the number of pages ...")
        href_list = tree.xpath(self.XPATH_DICT["href_links"])
        all_pages = [1]
        for href in href_list:
            if match_obj := re.search(r"&p=(\d+)", href):
                all_pages.append(int(match_obj.group(1)))
        return max(all_pages), result_list

    def crawl_filmography(self, url) -> list:
        new_url = f"{url}&role-cat=none&orderby=date-desc&v=slist&p=1"
        try:
            total_page, result_list = self.processe_single_page(new_url, check_total_pages=True)
        except Exception as e:
            raise Exception(f"COULD NOT GET: <total_page>, <result_list>: {e}")
        self.logger.info(f"<total_page>: {total_page}")
        if total_page == 1:
            return result_list
        for page in range(total_page+1, 2):
            new_url = f"{url}&role-cat=none&orderby=date-desc&v=slist&p={page}"
            result_list += self.processe_single_page(url)
            time.sleep(random.uniform(1, 3))
        return result_list
