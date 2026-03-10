# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from urllib.parse import parse_qs, urlparse


class ProductsPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Normalize whitespace for text fields
        for field in ("product_name", "brand"):
            value = adapter.get(field)
            if isinstance(value, str):
                adapter[field] = " ".join(value.split())

        # Clean price: remove "Rs. " prefix and normalize whitespace
        price = adapter.get("price")
        if isinstance(price, str):
            adapter["price"] = " ".join(price.replace("Rs.", "").split()).strip()

        # Convert Next.js image proxy URL to the original image URL.
        image_url = adapter.get("image_url")
        if isinstance(image_url, str):
            image_url = image_url.strip()
            if image_url.startswith("/_next/image?"):
                query = parse_qs(urlparse(image_url).query)
                real_url = query.get("url", [""])[0]
                if real_url:
                    adapter["image_url"] = real_url
            else:
                adapter["image_url"] = image_url

        return item
