from logging import Logger

from src import constants
from src.parser_mixin import ParserMixin
from src import utils
from lxml.html import HtmlElement


class Scraper(ParserMixin):
    FILM_XPATH_DICT = {
        "data_movie_id": '//div[@id="item2item"]/@data-movie-id',
        "dd_list": '//div[@id="left-column"]/dl[1]/dt/following-sibling::dd',
    }

    NAME_XPATH_DICT = {
        "name": '//h1[@id="main-title"]/a/@content',
        "attribute": '//div/strong/following-sibling::div[1]',
        "filmography": ('//h1[@id="main-title"]/../following-sibling::div'
                        '//ul/li/a[contains(@href, "name-movies.php")]/@href'),
    }
    MATCH_KEYS = {
        "original title": "original_title",
        "datepublished": "date_published",
        "duration": "duration",
        "country": "country",
        "director": "director",
        "screenwriter": "screenwriter",
        "cast": "cast",
        "music": "music",
        "cinematography": "cinematography",
        "producer": "producer",
        "genre": "genre",
        "movie groups": "movie_groups",
        "description": "description",
        "data_movie_id": "data_movie_id"
    }

    def __init__(self, base_logger: Logger) -> None:
        self.logger = utils.adapter_log(base_logger, {"worker_id": "SCRAPER"})
        self.configure_parser()

    def scrape_name(self, url: str) -> dict:
        self.logger.info(f"Scraping name from {url}")
        tree = self.get_tree(url)
        result = {}
        elements = tree.xpath(self.NAME_XPATH_DICT["name"])
        if elements == []:
            raise Exception('XPATH <name> DOES NOT WORK')
        result["name"] = elements[0]

        elements = tree.xpath(self.NAME_XPATH_DICT["filmography"])
        if elements == []:
            raise Exception('XPATH <name> DOES NOT WORK')

        result["filmography_url"] = elements[0]
        self.logger.info(f"Looking for attributes")
        for att in tree.xpath(self.NAME_XPATH_DICT["attribute"]):
            value = att.text_content().strip()
            if value == "":
                value = att.xpath("./a/@href")
            key = att.xpath("preceding-sibling::strong[1]")[0].text_content().strip()
            key = key.replace(":", "").lower()
            print(f"{key}::: {value}")
            result[key] = value
        result["name_id"] = utils.get_parameter_from_url(url, "name-id")
        return result

    def get_clean_result(self, result: dict) -> dict:
        clean_result = {}
        for k, v in self.MATCH_KEYS.items():
            clean_result[v] = result[k] if k in result else None
            clean_result["extra_keys"] = {}
            for k, v in result.items():
                if k in self.MATCH_KEYS:
                    continue
                clean_result["extra_keys"][k] = v
        return clean_result

    def process_dd(self, dd: HtmlElement) -> dict:
        extra_data = {}
        key = dd.xpath("preceding-sibling::dt[1]")[0].text_content()
        key = key.strip().lower()
        if len(dd) == 0:
            extra_data[key] = dd.text_content().strip()
            return extra_data
        if not (anchor_list := dd.xpath('.//a')):
            extra_data[key] = dd.text_content().strip()
            return extra_data
        values = []
        for a in anchor_list:
            attrib = dict(a.attrib)
            if "class" in attrib:
                attrib.pop("class")
            if "itemprop" in attrib:
                attrib.pop("itemprop")
            if len(attrib) == 1:
                attrib["title"] = a.text.strip()
            values.append(attrib)
        extra_data[key] = values
        return extra_data

    def scrape_film(self, url: str) -> dict:
        self.logger.info(f"Scraping film from {url}")
        tree = self.get_tree(url, kwargs={"headers": constants.HEADERS})
        elements = tree.xpath(self.FILM_XPATH_DICT["data_movie_id"])
        if elements == []:
            raise Exception('XPATH <data_movie_id> DOES NOT WORK')
        result = {}
        result["data_movie_id"] = elements[0]
        dd_list = tree.xpath(self.FILM_XPATH_DICT["dd_list"])
        for index, dd in enumerate(dd_list, 1):
            if itemprop := dd.attrib.get("itemprop", None):
                itemprop = itemprop.lower()
                result[itemprop] = dd.text_content().strip()
                continue
            extra_data = self.process_dd(dd)
            result.update(extra_data)

        self.logger.info(f"Getting <clean_result> ...")
        clean_result = self.get_clean_result(result)
        clean_result["url"] = url
        return clean_result
