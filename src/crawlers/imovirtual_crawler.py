"""
A class for extracting data from the Imovirtual site.

URL guide:
- Base URL: 'https://www.imovirtual.com/pt/resultados/'
- Query options for extraction:
    Base URL + offer_type/property_type/location/sub_location
    - offer_type: 'comprar' | 'arrendar'
    - property_type:
        - 'apartamento'
        - 't0' (Studio)
        - 'moradia' (House)
        - 'quarto' (only with offer_type='arrendar')
        - 'terreno' (Land)
        - 'imoveis-comerciais' (Commercial properties)
        - 'armazens' (Warehouses)
        - 'garagem' (Garage)
    - location: Portugal District
        | 'todo-o-pais' (entire country, sub_location must be '' in this case)
    - sub_location: Portugal Council | ''
- Example for extracting from the entire country:
    base_url + /comprar/moradia/todo-o-pais
"""

import itertools
from datetime import datetime
from http import HTTPStatus

import pandas as pd
import requests
from bs4 import BeautifulSoup

from src.config.settings import Settings
from src.crawlers.default_crawler import AbstractCrawler


class ImovirtualCrawler(AbstractCrawler):
    def __init__(self) -> None:
        super().__init__(site_name='imovirtual')
        self.base_url = 'https://www.imovirtual.com/pt/resultados/'
        self.params = {'page': self.page, 'limit': 72}

    def crawl(
        self,
        offer_types: list[str] = ['comprar'],
        property_types: list[str] = ['lisboa'],
        locations: list[str] = [''],
        sub_locations: list[str] = [''],
    ):
        combinations = list(
            itertools.product(
                offer_types, property_types, locations, sub_locations
            )
        )

        for item in combinations:
            self.data = []
            self.page = 1
            self.params['page'] = self.page
            self.url_args = item
            self.start_url_session()

        self.final_df = pd.concat(self.list_dfs, ignore_index=True, axis=0)

        if Settings().SAVE_TO_MONGO:
            self.save_data(self.final_df)
        if Settings().LOCAL_STORAGE:
            self.export_parquet_file(self.final_df)

    def start_url_session(self):
        (
            self.offer_type,
            self.property_type,
            self.location,
            self.sub_location,
        ) = [*self.url_args]

        self.url = (
            f'{self.base_url}{self.offer_type}/'
            f'{self.property_type}/{self.location}'
        )

        if self.sub_location:
            self.url = f'{self.url}/{self.sub_location}'

        with requests.Session() as session:
            print('Crawler Started')
            self.validate_request(session)
            self.extract_data()
            next_page = self.has_next_page()

            while next_page:
                self.page += 1
                self.params['page'] = self.page
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
            raise SystemExit(
                f'Error: Received status code != 200 ({s.status_code})'
            )

        html = s.text
        self.soup = BeautifulSoup(html, 'html.parser')

    def has_next_page(self):
        """
        Return True if there is more data to extract on the next page
        and False if not.

        Single page case:
            - If soup.find('li', title='Go to next Page') is None

        Multi-page case:
            - First page:
                soup.find(
                    'li', title='Go to next Page'
                )['aria-disabled'] == 'false'
            - Intermediate pages:
                soup.find(
                    'li', title='Go to next Page'
                )['aria-disabled'] == 'false'
            - Last page:
                soup.find(
                    'li', title='Go to next Page'
                )['aria-disabled'] == 'true'

        Logic:
            - If the button does not exist, it is the first page.
            - If the button exists, check
                soup.find(
                    'li', title='Go to next Page'
                )['aria-disabled'] != 'true' (or == 'false') to continue.
        """

        next_page_button = self.soup.find('li', title='Go to next Page')

        if next_page_button:
            return next_page_button['aria-disabled'] == 'false'
        else:
            return False

    def extract_data(self):
        contents = self.soup.find_all('article')

        for content in contents:
            title = content.find(attrs={'data-cy': 'listing-item-title'}).text
            price = content.find(attrs={'direction': 'horizontal'}).text
            try:  # css class changes! Check if all records are None
                location = content.find('p', class_='css-42r2ms eejmx80').text
            except Exception:
                location = None
            link = content.find('a').get('href')
            info_agg = [info.text for info in content.find_all('dd')]

            self.data.append({
                'title': title,
                'price_euro': price,
                'location': location,
                'link': link,
                'info_agg': info_agg,
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
    offer_types_search = [
        # 'comprar',
        'arrendar'
    ]
    property_types_search = [
        # 'apartamento',
        'moradia'
    ]
    location_search = ['lisboa']
    sub_location_search = ['']

    ImovirtualCrawler().crawl(
        offer_types=offer_types_search,
        property_types=property_types_search,
        locations=location_search,
        sub_locations=sub_location_search,
    )
