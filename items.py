from scrapy.item import Item, Field


class NoticeItem(Item):
    title = Field()
    notice = Field()
    notice_code = Field()
    category = Field()
    publish_date = Field()
