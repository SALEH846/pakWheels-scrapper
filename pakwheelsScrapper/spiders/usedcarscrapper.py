import scrapy
from scrapy import Request

class UsedCarsSpider(scrapy.Spider):
    name = 'usedcars' # name of crawler
    base_url = "https://www.pakwheels.com"
    start_urls = ["https://www.pakwheels.com/used-cars/search/-/"]

    def parse(self, response):

        # links of pages of all vehicles on the current page will be stored in this list
        links = []

        # Extract all the links of pages of all vehicles availale for sale on current page one by one and append them to `links` list
        for car in response.css('a.car-name.ad-detail-path'):
            links.append(self.base_url + car.css('a.car-name.ad-detail-path').attrib['href'])

        # Then iterate over all the links one by one and extract the required information
        for url in links:
            yield Request(url=url, callback=self.parse_details)

        # extract the link of next page and scrape the data of all cars on that page
        next_page = response.xpath('//li[@class="next_page"]/a/@href').get()
        if next_page is not None:
            yield response.follow("https://www.pakwheels.com" + next_page, callback=self.parse)


    def parse_details(self, response):

        # name of the individual vehicle
        name = response.xpath('//div[@id="scroll_car_info"]/h1/text()').get()

        # location of the vehicle
        location = response.xpath('//div[@id="scroll_car_info"]/p/a/text()').get().strip()

        # check if the table has five columns
        if len(response.xpath('//table[@class="table table-bordered text-center table-engine-detail fs16"]//tbody//tr//td//p//text()').getall()) == 5:
            # model of the vehicle
            model =  response.xpath('//table[@class="table table-bordered text-center table-engine-detail fs16"]//tbody//tr//td//p//text()').getall()[0]
            # mileage of the vehicle
            mileage =  response.xpath('//table[@class="table table-bordered text-center table-engine-detail fs16"]//tbody//tr//td//p//text()').getall()[2]
            # Type of engine of the vehicle
            engine_type =  response.xpath('//table[@class="table table-bordered text-center table-engine-detail fs16"]//tbody//tr//td//p//text()').getall()[3]
            # Type of the transmission of the vehicle
            transmission =  response.xpath('//table[@class="table table-bordered text-center table-engine-detail fs16"]//tbody//tr//td//p//text()').getall()[4]
        # if the table has 4 columns
        else:
            # model of the vehicle
            model =  response.xpath('//table[@class="table table-bordered text-center table-engine-detail fs16"]//tbody//tr//td//p//text()').getall()[0]
            model = model.strip()
            # mileage of the vehicle
            mileage =  response.xpath('//table[@class="table table-bordered text-center table-engine-detail fs16"]//tbody//tr//td//p//text()').getall()[1]
            # Type of engine of the vehicle
            engine_type =  response.xpath('//table[@class="table table-bordered text-center table-engine-detail fs16"]//tbody//tr//td//p//text()').getall()[2]
            # Type of the transmission of the vehicle
            transmission =  response.xpath('//table[@class="table table-bordered text-center table-engine-detail fs16"]//tbody//tr//td//p//text()').getall()[3]

        # Place where the vehicle is registered
        registered_in = response.xpath('//ul[@id="scroll_car_detail"]/li//text()').getall()[1]
        # color of the vehicle
        color = response.xpath('//ul[@id="scroll_car_detail"]/li//text()').getall()[3]
        # Whether the assembly of the vehicle is local or imported
        assembly = response.xpath('//ul[@id="scroll_car_detail"]/li//text()').getall()[5]
        # Maximum engine capacity of the vehicle
        engine_capacity = response.xpath('//ul[@id="scroll_car_detail"]/li//text()').getall()[7]
        # Type pf body of the vehicle
        body_type = response.xpath('//ul[@id="scroll_car_detail"]/li//text()').getall()[9]
        # url of the vehicle
        url = response.url

        # Check if the table of extra features exists
        if response.xpath('//ul[@class="list-unstyled car-feature-list nomargin"]/li//text()'):
            # List of all the extra features in the vehicle
            list_of_other_features = response.xpath('//ul[@class="list-unstyled car-feature-list nomargin"]/li//text()').getall()
            list_of_other_features = [i.strip() for i in list_of_other_features]
        # if table of extra features doesn't exist
        else:
            # fill the `list_of_other_features` variable as `N/A` i.e. not available
            list_of_other_features = "N/A"
        
        # Check if the price of vehicle exists
        if response.xpath('//div[@class="price-box"]/strong/span/text()').get():
            # price of teh vehicle
            price = response.xpath('//div[@class="price-box"]/strong/text()').get() + response.xpath('//div[@class="price-box"]/strong/span/text()').get()
        # if price doesn't exists
        else:
            # fill the `price` variable as `N/A` i.e. not available
            price = "N/A"

        # Phone number of the seller
        phone = "+92" + response.xpath('//input[@id="mobile-number"]/@placeholder').get()

        # return all the features of each vehicle
        yield {
            'name': name,
            'location': location,
            'model_year': model,
            'mileage': mileage,
            'engine_type': engine_type,
            'transmission': transmission,
            'registered_in': registered_in,
            'color': color,
            'assembly': assembly,
            'engine_capacity': engine_capacity,
            'body_type': body_type,
            'other_features_list': list_of_other_features,
            'url': url,
            'price': price,
            "phone_number": phone
        }