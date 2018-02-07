# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import HtmlXPathSelector
from Dronation.items import DronationItem

class DronepowerSpider(scrapy.Spider):
    name = 'DronePower'
    allowed_domains = ['https://www.powerbuy.co.th/']
    start_urls = ['https://www.powerbuy.co.th/en/smart-tech-and-gadgets/smart-toys-and-gadgets/drones/']

    # def parse(self, response):
    #     SET_SELECTOR = 'div.product-item'
    #     for drone in response.xpath(SET_SELECTOR):
    #         IMAGE_SELECTOR = '//*[@id="maincontent"]/div[3]/div[1]/div[3]/ol/li/div/div/a/span/span/img/@src'
    #         PRODUCT_SELECTOR = '//*[@id="maincontent"]/div[3]/div[1]/div[3]/ol/li/div/div/div/div/strong/a/text()'
    #         DESCRIPTION_SELECTOR = '//*[@id="maincontent"]/div[3]/div[1]/div[3]/ol/li/div/div/div/div/div/text()'
    #         PRICE_SELECTOR = '//*[@id="maincontent"]/div[3]/div[1]/div[3]/ol/li/div/div/div//span[@class="price"]/text()'
    #
    #         yield {
    #             'image': drone.xpath(IMAGE_SELECTOR).extract(),
    #             'product': drone.xpath(PRODUCT_SELECTOR).extract(),
    #             'description': drone.xpath(DESCRIPTION_SELECTOR).extract(),
    #             'price': drone.xpath(PRICE_SELECTOR).extract(),
    #         }
    #
    #     print(dict('image = Image', 'product = Product', 'description = Description', 'price = Price'))


    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        drones = hxs.select('//*[@id="maincontent"]/div[3]/div[1]/div[3]/ol/li/div')
        items = []
        for drone in drones:
            item = DronationItem()
            item["Image"] = drones.select('//*[@id="maincontent"]/div[3]/div[1]/div[3]/ol/li/div/div/a/span/span/img/@src').extract()
            item["Product"] = drones.select('//*[@id="maincontent"]/div[3]/div[1]/div[3]/ol/li/div/div/div/div/strong/a/text()').extract()
            item["Description"] = drones.select('//*[@id="maincontent"]/div[3]/div[1]/div[3]/ol/li/div/div/div/div/div/text()').extract()
            item["Price"] = drones.select('//*[@id="maincontent"]/div[3]/div[1]/div[3]/ol/li/div/div/div//span[@class="price"]/text()').extract()
            items.append(item)
        return items

        # for drone in drones:
        #     # image = drones.select('//*[@id="maincontent"]/div[3]/div[1]/div[3]/ol/li/div/div/a/span/span/img/@src').extract()
        #     # product = drones.select('//*[@id="maincontent"]/div[3]/div[1]/div[3]/ol/li/div/div/div/div/strong/a/text()').extract()
        #     # description = drones.select('//*[@id="maincontent"]/div[3]/div[1]/div[3]/ol/li/div/div/div/div/div/text()').extract()
        #     # price = drones.select('//*[@id="maincontent"]/div[3]/div[1]/div[3]/ol/li/div/div/div//span[@class="price"]/text()').extract()
        #     # print image, product, description, price


    def parse_item_link(self, response):
        for href in response.css('//*[@id="maincontent"]/div[3]/div[1]/div[3]/ol/li/div'):
            url = str(href.extract()).strip()
            yield scrapy.Request(url, callback=self.parse_detail_page)


    def parse_detail_page(self, response):
        product = DronationItem()
        product['image'] = response.css('h1 span.a-size-large::text').extract()
        product['url'] = response.url

        if response.xpath('//*[@id="maincontent"]/div[3]/div[1]/div[3]/ol/li/div/div/a/span/span/img/@src').re_first('\d+,*\d*d*d*') == None:
            product['Drone'] = response.xpath('//li[@id="Drone"]/text()').re_first('\d+,*\d*d*d*')
        else:
            product['Drone'] = response.xpath('//*[@id="maincontent"]/div[3]/div[1]/div[3]/ol/li/div/div/a/span/span/img/@src').re_first('\d+,*\d*d*d*')

        try:
            product['product'] = str(response.xpath(
                '''//*[@id="maincontent"]/div[3]/div[1]/div[3]/ol/li/div/div/div/div/strong/a/text()''').extract()[0]).strip()
        except IndexError:
            pass

        try:
            product['description'] = str(response.xpath(
                '''//*[@id="maincontent"]/div[3]/div[1]/div[3]/ol/li/div/div/div/div/div/text()''').extract()[1]).strip()
        except IndexError:
            pass
        try:
            product['price'] = response.css(
                'span.price::text').re('^[$]\d+\.\d+')[0]
        except IndexError:
            pass

        yield product


        NEXT_PAGE_SELECTOR = '.next a ::attr(href)'
        next_page = response.css(NEXT_PAGE_SELECTOR).extract_first()
        if next_page:
            yield scrapy.Request(
                response.urljoin(next_page),
                callback=self.parse
            )
