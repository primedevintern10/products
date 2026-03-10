import scrapy
from products.items import ProductsItem


class ProductSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["beautymart.lk"]
    start_urls = ["https://www.beautymart.lk/shop?filter_cat=body-care"]

    def parse(self, response):
        products = response.css('div.group.bg-white.rounded.overflow-hidden.border')
        
        for product in products:
            item = ProductsItem()
            
            item['product_name'] = product.css('h3::text').get()
            item['brand'] = product.css('span.text-xs::text').get()
            
            # Get price parts and join them
            price_parts = product.css('div.text-xl::text').getall()
            item['price'] = ''.join(price_parts).strip()
            
            # Get image URL
            item['image_url'] = product.css('img::attr(src)').get()
            
            yield item
