import scrapy
import json


class QuotesSpider(scrapy.Spider):
    name = "redpiso"
    global pag_base
    pag_base = "redpiso"
    global url
    url = "www.redpiso.es/"
    global data
    data = {}

    start_urls = [
        'https://www.redpiso.es/alquiler-viviendas/castellon',
    ]

    def parse(self, response):
        direction = response.xpath('//div[@class = "property-contact-item"]/h1//text()').extract_first()
        if direction:
            data = self._extract_data(response, direction)
            self._write_data(json.dumps(data))

        pages_other_sell = response.xpath('//div[@class = "tabbable-line"]//ul//li//a/@href').extract()
        pages_house = response.xpath('//div[@class = "property-list-location"]/h5//a//@href').extract()
        next_pages = pages_other_sell + pages_house
        if next_pages is not None:
            for page in next_pages:
                yield response.follow(page, callback=self.parse)

    # Get data of a house
    def _extract_data(self, response, dir):
        if "en venta en" in dir:
            street = dir.split("en venta en ", 1)[1]
            type_s = "Venta"
        elif "en alquiler en" in dir:
            street = dir.split("en alquiler en ", 1)[1]
            type_s = "Alquiler"
        else:
            street = dir.split("venta alquiler en ", 1)[1]
            type_s = "Venta/alquiler"

        price, price_measure = response.xpath('//div[@class = "property-contact-item"]/h2//text()').extract_first().split()
        size, size_measure = response.xpath('//div[@class = "property-icons"]//span[@class = "first"]//text()').extract_first().split()
        imgs = response.xpath('//div[@class = "col-lg-3 col-md-6 col-sm-6"]//a//img//@data-original').extract()
        data = {
            'street': street.encode("utf-8"),
            'type': type_s,
            'price': int(price.replace(".", "")),
            'currency': price_measure.encode("utf-8"),
            'size': int(size),
            'size_measure': size_measure.encode("utf-8"),
            'imgs': [url + img.encode("utf-8") for img in imgs]
        }
        return data

    # Write data in pag_base.json in json format
    def _write_data(self, data):
        import os
        fname = pag_base + ".json"
        fexists = os.path.isfile(fname)
        if fexists:
            file = open(fname, "r+")
            file.seek(os.path.getsize(fname) - 1, 0)  # Index last ']'
            data = ", " + data + "]"
        else:
            file = open(fname, "w")
            data = "[" + data + "]"

        file.write(data)
        file.close()
