"""
A class for extracting data from the Sapo Imóveis site.

When there are no results for a search, it returns a 404 error,
even if the URL is correct. This occurs when there are no properties
available in this specific location. Therefore, if it encounters
a 404 error here, we simply print the message.

URL guide:
- Base URL: 'https://casa.sapo.pt/'
- Query options for extraction:
        Base URL + offer_type-property_type/location/sub_location
  - offer_type: 'comprar' | 'alugar'
  - property_type:
    - 'apartamentos' (Apartments)
    - 'moradias' (Houses)
    - 'terrenos' (Land)
    - 'lojas' (Stores)
    - 'escritorios' (Offices)
    - 'predios' (Buildings)
    - 'armazens' (Warehouses)
    - 'imoveis-de-luxo' (Luxury properties) - only with offer_type='comprar'
    - 'quarto' (Room) - only with offer_type='alugar'
    - 'garagem' (Garage)
  - location: Portugal District | None
  - sub_location: Portugal Council | None
- Example for extracting from the entire country: base_url + /comprar-moradias
- Example of all kinds ot offer type and property type
in one specific location: base_url + /lisboa/
- Example of all kinds ot offer type and property type
in one specific location: base_url /distrito.lisboa/
"""

import itertools
from datetime import datetime
from http import HTTPStatus

import pandas as pd
import requests
from bs4 import BeautifulSoup

from src.crawlers.default_crawler import AbstractCrawler


class SapoCrawler(AbstractCrawler):
    def __init__(self) -> None:
        super().__init__(site_name='sapo')
        self.base_url = 'https://casa.sapo.pt/'
        self.params = {'pn': self.page}

    def crawl(
        self,
        offer_types: list[str] = ['comprar'],
        property_types: list[str] = [''],
        locations: list[str] = [''],
        sub_locations: list[str] = [''],
    ):
        self.check_before_crawl()

        combinations = list(
            itertools.product(
                offer_types, property_types, locations, sub_locations
            )
        )

        for item in combinations:
            self.data = []
            self.page = 1
            self.params = {'pn': self.page}
            self.url_args = item
            self.start_url_session()

        self.final_df = pd.concat(self.list_dfs, ignore_index=True, axis=0)

        if self.save_to_mongo:
            self.save_data(self.final_df)
        if self.local_storage:
            self.export_parquet_file(self.final_df)

    def start_url_session(self):
        (
            self.offer_type,
            self.property_type,
            self.location,
            self.sub_location,
        ) = [*self.url_args]

        self.url = f'{self.base_url}{self.offer_type}-{self.property_type}/'

        if self.location:
            self.url = f'{self.url}{self.location}/'
        if self.sub_location:
            self.url = f'{self.url}{self.sub_location}/'

        with requests.Session() as session:
            print('Crawler Started')
            self.validate_request(session)
            self.extract_data()
            next_page = self.has_next_page()

            while next_page:
                self.page += 1
                self.params = {'pn': self.page}
                self.validate_request(session)
                self.extract_data()
                next_page = self.has_next_page()

        self.add_features()

    def validate_request(self, session):
        s = session.get(
            self.url,
            headers=self.headers,
            params=self.params,
            hooks={'response': self.print_url},
        )

        if s.status_code != HTTPStatus.OK:
            print(f'Error: Received status code != 200 ({s.status_code})')

        html = s.text
        self.soup = BeautifulSoup(html, 'html.parser')

    def has_next_page(self):
        """
        Return True if there is more data to extract on the next page
        and False if not.

        Single page case:
            - soup.find("span", class_="disabled") is None

        Multi-page case:
            - First page:
                soup.find("span", class_="disabled").text == ' Anterior'
            - Intermediate pages:
                soup.find("span", class_="disabled") is None
            - Last page:
                soup.find("span", class_="disabled").text == ' Seguinte '

        Logic:
            - If the button does not exist and it is the first page,
            exit the while loop.
            - Now that we have ensured it is a multi-page case,
            return True until
                soup.find("span", class_="disabled").text == ' Seguinte '.
        """

        next_page_button = self.soup.find('span', class_='disabled')

        if not next_page_button and self.page == 1:  # onePage case
            return False

        if next_page_button:  # MultPage case
            return next_page_button.text != ' Seguinte '
        else:
            return True

    def extract_data(self):
        contents = self.soup.find_all('div', class_='property-info-content')

        for content in contents:
            title = content.find('div', class_='property-type').text
            price_euro = content.find(
                'div', class_='property-price-value'
            ).text
            location = content.find('div', class_='property-location').text
            link = content.find('a').get('href')
            info_agg = content.find(
                'div', class_='property-features-text'
            ).get_text()
            offer_type = content.find(
                'div', class_='property-price-type'
            ).get_text()

            self.data.append({
                'type': title,
                'location': location,
                'link': link,
                'price_euro': price_euro,
                'info_agg': info_agg,
                'offer_type': offer_type,
            })

    def add_features(self):
        df = pd.DataFrame(self.data)
        df = df.assign(site=self.site_name)
        df = df.assign(date_extracted=datetime.now().isoformat())
        df = df.assign(offer_type_search=self.offer_type)
        df = df.assign(property_type_search=self.property_type)
        df = df.assign(location_search=self.location)
        df = df.assign(sub_location_search=self.sub_location)
        print('Advertisements extracted:', df.shape[0])
        self.list_dfs.append(df)


if __name__ == '__main__':
    offer_types_search = ['comprar', 'alugar']
    property_types_search = ['apartamentos', 'moradias']
    location_search = ['distrito.lisboa']
    sub_location_search = ['']

    SapoCrawler().crawl(
        offer_types=offer_types_search,
        property_types=property_types_search,
        locations=location_search,
        sub_locations=sub_location_search,
    )
