from src.parser_mixin import ParserMixin
# from parser_mixin import ParserMixin
from src import utils

class Scraper(ParserMixin):
    FILM_XPATH_DICT = {
        "dd_list": '//div[@id="left-column"]/dl[1]/dt/following-sibling::dd',
    }
    FILM_DIRECT_OBTAINING = []
    NAME_XPATH_DICT = {
        "name": '//h1[@id="main-title"]/a/@content',
        "attribute": '//div/strong/following-sibling::div[1]',
        "filmography": ('//h1[@id="main-title"]/../following-sibling::div'
                        '//ul/li/a[contains(@href, "name-movies.php")]/@href'),
    }
    NAME_DIRECT_OBTAINING = []
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

    def __init__(self):
        self.configure_parser()

    def scrape_name(self, url):
        tree = self.get_tree(url)
        result = {}
        result["name"] = tree.xpath(self.NAME_XPATH_DICT["name"])[0]
        result["filmography_url"] = tree.xpath(self.NAME_XPATH_DICT["filmography"])[0]
        attribute_list = tree.xpath(self.NAME_XPATH_DICT["attribute"])
        for att in attribute_list:
            value = att.text_content().strip()
            if value == "":
                value = att.xpath("./a/@href")
            key = att.xpath("preceding-sibling::strong[1]")[0].text_content().strip()
            key = key.replace(":", "").lower()
            print(f"{key}::: {value}")
            result[key] = value
        result["name_id"] = utils.get_parameter_from_url(url, "name-id")
        return result

    def scrape_film(self, url) -> dict:
        result = {}
        headers = {'accept-language': 'en;q=0.9'}
        tree = self.get_tree(url, kwargs={"headers": headers})
        result["data_movie_id"] = tree.xpath('//div[@id="item2item"]/@data-movie-id')[0]
        dd_list = tree.xpath(self.FILM_XPATH_DICT["dd_list"])
        for index, dd in enumerate(dd_list, 1):
            if itemprop := dd.attrib.get("itemprop", None):
                itemprop = itemprop.lower()
                result[itemprop] = dd.text_content().strip()
                continue
            key = dd.xpath("preceding-sibling::dt[1]")[0].text_content()
            key = key.strip().lower()
            if len(dd) == 0:
                result[key] = dd.text_content().strip()
                continue
            if anchor_list := dd.xpath('.//a'):
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
                result[key] = values
            else:
                result[key] = dd.text_content().strip()
        clean_result = {}
        for k, v in self.MATCH_KEYS.items():
            if k in result:
                clean_result[v] = result[k]
            else:
                clean_result[v] = None
            clean_result["extra_keys"] = {}
            for k, v in result.items():
                if k in self.MATCH_KEYS:
                    continue
                clean_result["extra_keys"][k] = v
        clean_result["url"] = url
        return clean_result
