import json
import os

import scrapy
from scrapy.http.response.text import TextResponse

from .. import helpers

cwd = os.getcwd()


class DomainexplorerSpider(scrapy.Spider):
    """
    This spider is designed to find new domain names to which links exist from given host names.
    """
    name = 'domainexplorer'
    # TODO: generic start, include subdomains
    allowed_domains = ['veiliginternetten.nl']
    start_urls = ['https://veiliginternetten.nl/']
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
            curr_url, _ = helpers.strip_abs_url(response.request.url)
            rel_urls = dict()
            abs_domains = dict()

            for link in response.css('*::attr(href)'):

                tmp = link.get()

                if tmp.startswith('http'):
                    # Found an absolute URL
                    tmp, rel_path = helpers.strip_abs_url(tmp)
                    if tmp != curr_url:
                        abs_domains[tmp] = response.request.url
                    elif rel_path:
                        rel_urls[rel_path] = response.request.url
                elif tmp.startswith('/'):
                    # Found a relative URL
                    rel_urls[tmp] = response.request.url

            # Save our new findings
            # file_exists = os.path.isfile(f'{cwd}/govspider/domains/websites/{curr_url}.txt')
            # if not file_exists:
            #     open(f'{cwd}/govspider/domains/websites/{curr_url}.txt', 'a').close()
            # with open(f'{cwd}/govspider/domains/websites/{curr_url}.txt', 'r+') as f:
            #     for i in rel_urls:
            #         f.seek(0)
            #         for line in f:
            #             if line.startswith(f'{i} '):
            #                 break
            #         else:
            #             f.write(f'{i} ({rel_urls[i]})\n')

            with open(f'{cwd}/govspider/domains/new.txt', 'r+') as f:
                with open(f'{cwd}/govspider/domains/gov.txt', 'r') as gov_f:
                    for i in abs_domains:
                        gov_f.seek(0)
                        f.seek(0)
                        for line in gov_f:
                            if line.startswith(f'{i}'):
                                break
                        else:
                            for line in f:
                                if line.startswith(f'{i} '):
                                    break
                            else:
                                f.write(f'{i} ({abs_domains[i]})\n')

            # For all relative URLs found, we start a new request
            # Duplicates are filtered by Scrapy
            for url in rel_urls:
                if not url.endswith('.pdf'):
                    yield scrapy.Request(response.urljoin(url), callback=self.parse)
