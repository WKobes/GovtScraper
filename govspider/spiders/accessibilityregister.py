import os

import scrapy
from scrapy.http.response.text import TextResponse

from .. import helpers

cwd = os.getcwd()


class AccessibilityRegisterSpider(scrapy.Spider):
    """
    Quick scraper to download URLs from the toegankelijkheidsverklaring.nl
    """
    name = 'accessibilityregister'
    allowed_domains = ['toegankelijkheidsverklaring.nl']
    start_urls = [f'https://toegankelijkheidsverklaring.nl/register']
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
                'errors-accessibiltiy.txt',
                f'{response.url} - (Status {response.status}) - ({response.request.url})\n',
                f'{response.url} '
            )

        elif isinstance(response, TextResponse):

            for link in response.xpath("//a[text()='Bekijk verklaring']/@href"):
                yield scrapy.Request(response.urljoin(link.get()), callback=self.parse_accessibility_page)

            for x in response.xpath("(//span[text()='Volgende pagina']/parent::*/@href)[1]"):
                yield scrapy.Request(response.urljoin(x.get()), callback=self.parse)

    def parse_accessibility_page(self, response):
        """
        Parse individual accessibility register pages
        :param response:
        :return:
        """
        website = response.xpath("//a[@itemprop='website-url']/@href")
        # Save our new findings

        website = website.get()
        if website:
            website, _ = helpers.strip_abs_url(website)

            file_exists = os.path.isfile(f'{cwd}/govspider/domains/typen/domains_accessibility.txt')
            if not file_exists:
                open(f'{cwd}/govspider/domains/typen/domains_accessibility.txt', 'a').close()
            with open(f'{cwd}/govspider/domains/typen/domains_accessibility.txt', 'r+') as f:
                f.seek(0)
                for line in f:
                    if line.startswith(f'{website}'):
                        break
                else:
                    f.write(f'{website}\n')
