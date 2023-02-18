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
    allowed_domains = ['']  # Domain(s) allowed in this crawl
    start_urls = ['']  # Starting URLs (usually homepage of every website)
    handle_httpstatus_list = [400, 403, 404, 500]

    @staticmethod
    def write_to(file, entry, check):
        with open(f'{cwd}/govspider/domains/{file}', 'r+') as f:
            for line in f:
                if line.startswith(check):
                    break
            else:
                f.write(entry)
        return

    def parse(self, response):
        """

        :param response:
        :return:
        """
        if response.status != 200:
            if response.status != 200:
                self.write_to(
                    'errors.txt',
                    f'{response.url} - (Status {response.status}) - ({response.request.url})\n',
                    f'{response.url} '
                )

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

            with open(f'{cwd}/govspider/domains/new.txt', 'r+') as f:
                with open(f'{cwd}/govspider/domains/gov.txt', 'r') as gov_f:
                    for i in abs_domains:
                        gov_f.seek(0)
                        f.seek(0)
                        for line in gov_f:
                            if line.startswith(f'{i}'):
                                break
                            elif '.' + line.rstrip() in i:
                                with open(f'{cwd}/govspider/domains/verified.txt', 'r+') as f2:
                                    for sub in f2:
                                        if sub.startswith(f'{i}'):
                                            break
                                    else:
                                        f2.write(f"{i}\n")
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
                if not url.endswith('.pdf') and not any(string in url for string in ['%5D=created', '%5D=bibcite_year', '%5D=sdv_published', '%5D=search_subjects']):
                    yield scrapy.Request(response.urljoin(url), callback=self.parse)
