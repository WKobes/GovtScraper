import os

import scrapy
from scrapy.http.response.text import TextResponse

from .. import helpers

cwd = os.getcwd()


SETTING_TYPE = 'bundes'  # All


class BundesBehordenSpider(scrapy.Spider):
    """
    Quick scraper to download URLs from https://www.service.bund.de
    """
    name = 'bundesbehorden'
    allowed_domains = ['www.service.bund.de']
    start_urls = [f'https://www.service.bund.de/Content/DE/Behoerden/Suche/Formular.html?resultsPerPage=100']
    handle_httpstatus_list = [400, 403, 404, 500]

    def write_to(self, file, entry, check):
        with open(f'{cwd}/govspider/domains/{file}', 'r+') as f:
            for line in f:
                if line.startswith(check):
                    break
            else:
                f.write(entry)
        return

    def parse(self, response):
        """
        Parse pages of search results
        :param response:
        :return:
        """
        if response.status != 200:
            self.write_to(
                'errors.txt',
                f'{response.url} - (Status {response.status}) - ({response.request.url})\n',
                f'{response.url} '
            )

        elif isinstance(response, TextResponse):

            for link in response.xpath("//ul[@class='result-list']/li/a/@href"):
                yield scrapy.Request(response.urljoin(link.get()), callback=self.parse_almanak_page)

            for x in response.xpath("(//li[@class='next']/a/@href)[1]"):
                yield scrapy.Request(response.urljoin(x.get()), callback=self.parse)

    def parse_almanak_page(self, response):
        """
        Parse individual organization pages
        :param response:
        :return:
        """
        website = response.xpath("(//a[@class='external']/@href)[1]")
        # Save our new findings

        website = website.get()
        if website:
            website, _ = helpers.strip_abs_url(website)

            file_exists = os.path.isfile(f'{cwd}/govspider/domains/typen/domains_{SETTING_TYPE}.txt')
            if not file_exists:
                open(f'{cwd}/govspider/domains/typen/domains_{SETTING_TYPE}.txt', 'a').close()
            with open(f'{cwd}/govspider/domains/typen/domains_{SETTING_TYPE}.txt', 'r+') as f:
                f.seek(0)
                for line in f:
                    if line.startswith(f'{website}'):
                        break
                else:
                    f.write(f'{website}\n')
