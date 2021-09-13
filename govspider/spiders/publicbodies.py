import os

import scrapy
from scrapy.http.response.text import TextResponse

from .. import helpers

cwd = os.getcwd()

# SETTING_TYPE = 'Adviescollege'
# SETTING_TYPE = 'Agentschap'
# SETTING_TYPE = 'Caribisch%2520openbaar%2520lichaam'
# SETTING_TYPE = 'Gemeenschappelijke%2520regeling'
# SETTING_TYPE = 'Gemeente'
# SETTING_TYPE = 'Grensoverschrijdend%2520regionaal%2520samenwerkingsorgaan'
# SETTING_TYPE = 'Hoog%2520College%2520van%2520Staat'
# SETTING_TYPE = 'Interdepartementale%2520commissie'
# SETTING_TYPE = 'Kabinet%2520van%2520de%2520Koning'
# SETTING_TYPE = 'Koepelorganisatie'
# SETTING_TYPE = 'Ministerie'
# SETTING_TYPE = 'Openbaar%2520lichaam%2520voor%2520beroep%2520en%2520bedrijf'
# SETTING_TYPE = 'Organisatie%2520met%2520overheidsbemoeienis'
# SETTING_TYPE = 'Organisatieonderdeel'
# SETTING_TYPE = 'Politie%2520en%2520brandweer'
# SETTING_TYPE = 'Provincie'
# SETTING_TYPE = 'Rechtspraak'
# SETTING_TYPE = 'Regionaal%2520samenwerkingsorgaan'
# SETTING_TYPE = 'Waterschap'
SETTING_TYPE = 'Zelfstandig%2520bestuursorgaan'


class PublicbodiesSpider(scrapy.Spider):
    """
    Quick scraper to download URLs from the almanak.overheid.nl
    """
    name = 'publicbodies'
    allowed_domains = ['almanak.overheid.nl', 'overheid.nl']
    start_urls = [f'https://www.overheid.nl/zoekresultaat/contactgegevens-overheden/1/200/lijst/type={SETTING_TYPE}']
    handle_httpstatus_list = [400, 403, 404, 500]

    def parse(self, response):
        """

        :param response:
        :return:
        """
        if response.status != 200:
            with open(f'{cwd}/govspider/domains/errors.txt', 'r+') as f:
                for line in f:
                    if line.startswith(f'{response.url} '):
                        break
                else:
                    f.write(f'{response.url} - (Status {response.status}) - ({response.request.url})\n')

        elif isinstance(response, TextResponse):

            for link in response.xpath('//div[@class="result--list result--list--wide"]//a/@href'):
                yield scrapy.Request(link.get(), callback=self.parse_almanak_page)

            for x in response.xpath("(//span[text()='»']/parent::*/@href)[1]"):
                yield scrapy.Request(response.urljoin(x.get()), callback=self.parse)

    def parse_almanak_page(self, response):
        """

        :param response:
        :return:
        """
        website = response.xpath("//td[@data-before='Internet']/a/@href")
        # Save our new findings

        website = website.get()
        if website:
            website, _ = helpers.strip_abs_url(website)

            file_exists = os.path.isfile(f'{cwd}/govspider/domains/typen/{SETTING_TYPE}.txt')
            if not file_exists:
                open(f'{cwd}/govspider/domains/typen/{SETTING_TYPE}.txt', 'a').close()
            with open(f'{cwd}/govspider/domains/typen/{SETTING_TYPE}.txt', 'r+') as f:
                f.seek(0)
                for line in f:
                    if line.startswith(f'{website}'):
                        break
                else:
                    f.write(f'{website}\n')
