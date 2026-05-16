import os
import re
from string import Template

from src.crawler import Crawler
from src.scraper import Scraper
from src import constants
from src import utils


class Orchestrator:
    FILM_PATTERN = re.compile(r"filmaffinity.com/\w\w/film(\d+).html")
    NAME_PATTERN = re.compile(r"filmaffinity.com/\w\w/name.php\?name-id=(\d+)")
    WARNING_NAME_ID = Template("<name_id> is already in <names_result_dict>: $_id").substitute
    WARNING_DM_ID = Template("<data_movie_id> is already in <films_result_dict>: $_id").substitute
    FILMS_RESULT_PATH = utils.join_names([constants.FILE_DIR, "films_results.json"])
    NAMES_RESULT_PATH = utils.join_names([constants.FILE_DIR, "names_results.json"])

    def __init__(self, input_list: list):
        self.base_logger = utils.init__logger(constants.LOG_NAME)
        self.logger = utils.adapter_log(self.base_logger, {"worker_id": 'MAIN'})
        self.input_list = input_list
        self.names_result_dict = {}
        self.films_result_dict = {}

    @property
    def total_titles(self): return len(self.input_list)

    def checking_file_dir(self) -> None:
        dir_path = utils.join_names(constants.FILE_DIR)
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
            self.logger.warning(f"FILE_DIR was created: {dir_path}")

    def process_director(self, item: dict, scraper: Scraper, crawler: Crawler) -> None:
        director_url = item["href"]
        name_id = utils.get_parameter_from_url(director_url, "name-id")
        if name_id in self.names_result_dict:
            self.logger.warning(self.WARNING_NAME_ID(name_id=name_id))
            return
        self.logger.info(f"Scraping name: {director_url}")
        item_director = scraper.scrape_name(director_url)
        filmography_url = item_director["filmography_url"]
        self.logger.info(f"Crawling filmography: {filmography_url}")
        filmography = crawler.crawl_filmography(filmography_url)
        item_director["filmography"] = []
        for film in filmography:
            data_movie_id = film["data_movie_id"]
            item_director["filmography"].append(data_movie_id)
            if data_movie_id in self.films_result_dict:
                self.logger.warning(self.WARNING_DM_ID(_id=data_movie_id))
                continue
            film["full_details"] = False
            self.films_result_dict[data_movie_id] = film
        item_director["full_details"] = True
        item_director["url"] = director_url
        self.names_result_dict[name_id] = item_director

    def main_from_title_to_director(self, film_urls: list) -> None:
        total_films = len(film_urls)
        for index, url in enumerate(film_urls, 1):
            current = f"{index}/{total_films}: {url}"
            self.logger.info(f"Processing {current}")
            scraper = Scraper()
            crawler = Crawler()
            self.logger.info("Scraping film ...")
            result = scraper.scrape_film(url)
            data_movie_id = result["data_movie_id"]
            result["full_details"] = True
            self.films_result_dict[data_movie_id] = result
            for item in result["director"]:
                try:
                    self.process_director(item, scraper, crawler)
                except Exception as e:
                    self.logger.error(f"COULD NOT COMPLETE - {current}: {e}")

    def main_from_director_to_title(self, names_urls: list):
        scraper = Scraper()
        crawler = Crawler()
        result_dict = {}
        total_names = len(names_urls)
        for index, url in enumerate(names_urls, 1):
            self.logger.info(f"Processing {index}/{total_names}: {url}")
            name_id = utils.get_parameter_from_url(url, "name-id")
            if name_id in self.names_result_dict:
                self.logger.warning(self.WARNING_NAME_ID(_id=name_id))
                continue
            self.logger.info("Scraping name ...")
            item = scraper.scrape_name(url)
            filmography_url = item["filmography_url"]
            self.logger.info(f"Crawling filmography: {filmography_url}")
            filmography = crawler.crawl_filmography(filmography_url)
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

    def main(self) -> None:
        self.logger.info("START Orchestrator")
        self.checking_file_dir()
        self.logger.info(f"Total INPUTs: {self.total_titles}")
        film_urls = []
        names_urls = []
        for url in self.input_list:
            if self.FILM_PATTERN.search(url):
                film_urls.append(url)
            if self.NAME_PATTERN.search(url):
                names_urls.append(url)
        self.logger.info(f"Total <film_urls>: {len(film_urls)}")
        self.logger.info(f"Total <names_urls>: {len(names_urls)}")
        try:
            self.main_from_title_to_director(film_urls)
        except Exception as e:
            self.logger.error(f"COULD NOT COMPLETE: <film_urls> processing: {e}")

        try:
            self.main_from_director_to_title(names_urls)
        except Exception as e:
            self.logger.error(f"{e}")
            self.logger.error(f"COULD NOT COMPLETE: <names_urls> processing: {e}")

        if self.films_result_dict:
            try:
                utils.save_json(self.FILMS_RESULT_PATH, self.films_result_dict)
                self.logger.info(f"<films_result_dict> was saved: {self.FILMS_RESULT_PATH}")
            except Exception as e:
                self.logger.error(f"COULD NOT BE SAVED: <films_result_dict>: {e}")
        else:
            self.logger.warning("<films_result_dict> is empty")

        if self.names_result_dict:
            try:
                utils.save_json(self.NAMES_RESULT_PATH, self.names_result_dict)
                self.logger.info(f"<names_result_dict> was saved: {self.NAMES_RESULT_PATH}")
            except Exception as e:
                self.logger.error(f"COULD NOT BE SAVED: <names_result_dict>: {e}")
        else:
            self.logger.warning("<names_result_dict> is empty")
        self.logger.info("END Orchestrator")
