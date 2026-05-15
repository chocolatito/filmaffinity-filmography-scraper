import re
from src.crawler import Crawler
from src.scraper import Scraper
from src import constants
from src import utils
# from crawler import Crawler
# from scraper import Scraper
# import constants
# import utils


class Orchestrator:
    FILM_PATTERN = re.compile(r"filmaffinity.com/\w\w/film(\d+).html")
    NAME_PATTERN = re.compile(r"filmaffinity.com/\w\w/name.php\?name-id=(\d+)")

    def __init__(self, input_list: list):
        self.base_logger = utils.init__logger(constants.LOG_NAME)
        self.logger = utils.adapter_log(self.base_logger, {"worker_id": 'MAIN'})
        self.input_list = input_list

    @property
    def total_titles(self): return len(self.input_list)

    def main_from_title_to_director(self):
        for index, url in enumerate(self.input_list, 1):
            scraper = Scraper()
            crawler = Crawler()
            results = scraper.scrape_film(url)
            for item in results["director"]:
                director_url = item["href"]
                item_director = scraper.scrape_name(director_url)
                item["filmography"] = crawler.crawl_filmography(item_director["filmography_url"])
        file_path = utils.join_names(["results.json"])
        utils.save_json(file_path, results)

    def main_from_director_to_title(self):
        scraper = Scraper()
        crawler = Crawler()
        results = []
        for index, url in enumerate(self.input_list, 1):
            item = scraper.scrape_name(url)
            item["filmography"] = crawler.crawl_filmography(item["filmography_url"])
            results.append(item)
        file_path = utils.join_names(["results.json"])
        utils.save_json(file_path, results)

