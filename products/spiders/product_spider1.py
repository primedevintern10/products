import scrapy
from scrapy.http import HtmlResponse
from products.items import ProductsItem


class ProductSpider1(scrapy.Spider):
    name = "products1"
    allowed_domains = ["beautymart.lk"]
    start_urls = ["https://www.beautymart.lk/shop"]

    async def start(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                },
                callback=self.parse,
            )

    async def parse(self, response):
        page = response.meta["playwright_page"]

        # Wait for DOM and initial products to render
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_selector('div.group', timeout=15000)
        await page.wait_for_timeout(2000)

        # Scroll to bottom repeatedly until no new products load
        previous_count = 0
        max_attempts = 20  # safety limit
        attempts = 0

        while attempts < max_attempts:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)

            current_count = await page.evaluate(
                "() => document.querySelectorAll('div.group').length"
            )
            self.logger.info(f"Scroll attempt {attempts + 1}: found {current_count} products")

            if current_count == previous_count:
                break
            previous_count = current_count
            attempts += 1

        # Get final page content after all scrolling
        content = await page.content()
        await page.close()

        final_response = HtmlResponse(url=response.url, body=content, encoding='utf-8')
        products = final_response.css('div.group.bg-white.rounded.overflow-hidden.border')
        self.logger.info(f"Total products found: {len(products)}")

        for product in products:
            item = ProductsItem()

            item['product_name'] = product.css('h3::text').get()
            item['brand'] = product.css('span.text-xs::text').get()

            price_parts = product.css('div.text-xl::text').getall()
            item['price'] = ''.join(price_parts).strip()

            item['image_url'] = product.css('img::attr(src)').get()

            yield item
