import scrapy
from scrapy import Request

from python_assesment.items import NoticeItem


# Parsing class to handle all the parsing
class GazetteParseSpider:
    name = "gazette-parse"

    def parse(self, response):
        item = NoticeItem()
        item['title'] = self.notice_title(response)
        item['notice'] = self.notice_content(response)
        item['notice_code'] = self.notice_code(response)
        item['category'] = self.notice_category(response)
        item['publish_date'] = self.notice_publish_date(response)

        return item

    def notice_content(self, response):
        notice = response.css("div[data-gazettes='P'] p::text").getall()
        if notice is not None:
            cleaned_notice = ' '.join(' '.join(item.split()) for item in notice)
            return cleaned_notice
        return None

    def notice_publish_date(self, response):
        return response.css(".related-pane .notice-summary .metadata dd["
                            "property='gaz:hasPublicationDate'] time::text").get()

    def notice_category(self, response):
        return response.css(".category:nth-child(2)::text").get()

    def notice_code(self, response):
        return response.css(".related-pane .notice-summary .metadata dd["
                            "property='gaz:hasNoticeID']::text").get()

    def notice_title(self, response):
        return response.css(".main-pane .full-notice .title::text").get()


# Class for handling the crawling
class GazetteCrawlSpider(scrapy.Spider):
    name = "gazette-crawl"
    total_pages = 15
    parser = GazetteParseSpider()
    allowed_domains = ["thegazette.co.uk"]
    start_urls = ["https://www.thegazette.co.uk/all-notices"]
    pagination_url_t = "https://www.thegazette.co.uk/all-notices?results-page={param}"
    notice_url_t = "https://www.thegazette.co.uk{param}"

    def parse(self, response):
        # urls of 1 to 15 pages (pagination handling)
        yield from [
            Request(
                url=self.pagination_url_t.format(param=page),
                callback=self.parse_products
            )
            for page in range(1, self.total_pages)
        ]

    def parse_products(self, response):
        # handling the notices on each page
        notices_links = response.css(".notice-feed .content article .feed-item .btn-full-notice::attr(href)").getall()

        # list of all notices on single page
        params_list = [
            self.notice_url_t.format(param=notice_link)
            for notice_link in notices_links
        ]

        # making request to individual pages
        yield from [
            Request(
                url=url,
                callback=self.parse_product
            )
            for url in params_list
        ]

    def parse_product(self, response):
        # parsing the notice
        yield self.parser.parse(response)
