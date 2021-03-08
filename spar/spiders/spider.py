import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import SparItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class SparSpider(scrapy.Spider):
	name = 'spar'
	start_urls = ['https://www.sparbredebro.dk/nyheder/']

	def parse(self, response):
		articles = response.xpath('//article[contains(@id,"post-")]')
		for article in articles:
			date = article.xpath('.//p[@class="date"]/text()').get()
			post_links = article.xpath('.//h4/a/@href').getall()
			yield from response.follow_all(post_links, self.parse_post,cb_kwargs=dict(date=date))

	def parse_post(self, response,date):

		title = response.xpath('//h1/text()').get().strip()
		content = response.xpath('//article//text()[not (ancestor::h1)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))
		if not content:
			content = "Image at the URL"
		item = ItemLoader(item=SparItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
