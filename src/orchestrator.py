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
        self.names_result_dict = {}
        self.films_result_dict = {}

    @property
    def total_titles(self): return len(self.input_list)

    def main_from_title_to_director(self, film_urls: list):
        for index, url in enumerate(film_urls, 1):
            scraper = Scraper()
            crawler = Crawler()
            result = scraper.scrape_film(url)
            data_movie_id = result["data_movie_id"]
            result["full_details"] = True
            self.films_result_dict[data_movie_id] = result
            for item in result["director"]:
                director_url = item["href"]
                name_id = utils.get_parameter_from_url(director_url, "name-id")
                if name_id in self.names_result_dict:
                    continue
                item_director = scraper.scrape_name(director_url)
                filmography = crawler.crawl_filmography(item_director["filmography_url"])
                item_director["filmography"] = []
                for film in filmography:
                    data_movie_id = film["data_movie_id"]
                    item_director["filmography"].append(data_movie_id)
                    if data_movie_id in self.films_result_dict:
                        continue
                    film["full_details"] = False
                    self.films_result_dict[data_movie_id] = film
                item_director["full_details"] = True
                self.names_result_dict[name_id] = item_director

    def main_from_director_to_title(self, names_urls: list):
        scraper = Scraper()
        crawler = Crawler()
        result_dict = {}
        for index, url in enumerate(names_urls, 1):
            name_id = utils.get_parameter_from_url(url, "name-id")
            if name_id in self.names_result_dict:
                continue
            item = scraper.scrape_name(url)
            filmography = crawler.crawl_filmography(item["filmography_url"])
            item["filmography"] = []
            for film in filmography:
                data_movie_id = film.pop("data_movie_id")
                item["filmography"].append(data_movie_id)
                if data_movie_id not in self.films_result_dict:
                    film["full_details"] = False
                    self.films_result_dict[data_movie_id] = film
            item["url"] = url
            item["full_details"] = True
            self.names_result_dict[name_id] = item.copy()

    def main(self):
        self.logger.info("START")
        film_urls = []
        names_urls = []
        for url in self.input_list:
            if self.FILM_PATTERN.search(url):
                film_urls.append(url)
            if self.NAME_PATTERN.search(url):
                names_urls.append(url)
        self.main_from_title_to_director(film_urls)
        self.main_from_director_to_title(names_urls)
        utils.save_json("names_result_dict.json", self.names_result_dict)
        utils.save_json("films_result_dict.json", self.films_result_dict)
        self.logger.info("END")
