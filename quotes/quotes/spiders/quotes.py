# -*- coding: utf-8 -*-
import scrapy


class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    start_urls = ['https://cytaty24.pl/?pagec=1']

    def parse(self, response):
        for page in range(1, 1007):
            yield response.follow(f'https://cytaty24.pl/?pagec={page}', self.extract_quotes)

    def extract_quotes(self, response):
        for quote in response.xpath('//blockquote/p/text()').extract():
            yield {
                'quote': quote
            }
