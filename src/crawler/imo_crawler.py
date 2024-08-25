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


Json response guide:
    - List of items: json_data['props']['pageProps']['data']['searchAds']['items']
    - Promoted items: json_data['props']['pageProps']['data']['searchAdsRandomPromoted']['items']
    - Pagination: json_data['props']['pageProps']['data']['searchAds']['pagination']
"""

import itertools
import json
from http import HTTPStatus

import asyncio
import requests
from bs4 import BeautifulSoup
from httpx import AsyncClient, AsyncHTTPTransport
from requests.models import Response

from src.crawler.default_crawler import AbstractCrawler


class ImovirtualCrawler(AbstractCrawler):
    def __init__(self, site_name: str = 'imovirtual'):
        super().__init__(site_name)
        self.base_url = 'https://www.imovirtual.com/pt/resultados/'
        self.params = {'limit': 72}
    
    def crawl(
        self,
        offer_types: list[str] = ['comprar'],
        property_types: list[str] = ['lisboa'],
        locations: list[str] = [''],
        sub_locations: list[str] = [''],
    ):
        
        self.check_before_crawl()

        combinations = list(
            itertools.product(
                offer_types, property_types, locations, sub_locations
            )
        )

        for combination in combinations:
            (
                offer_type,
                property_type,
                location,
                sub_location,
            ) = [*combination]

            self.url = (
                f'{self.base_url}{offer_type}/'
                f'{property_type}/{location}'
            )

            if sub_location:
                self.url = f'{self.url}/{sub_location}'

            total_pages = self.get_number_of_pages()
            responses = self.fetch_all(total_pages=total_pages)
            list_ads = self.extract_ads(responses=responses)

            self.data.extend(list_ads)
        
        if self.save_to_mongo:
            ... # ToDo
            self.save_data(self.data)
        if self.local_storage:
            self.save_local_json()

    def get_number_of_pages(self) -> int:
        response = requests.get(self.url, params=self.params, headers=self.headers)
        if response.status_code != HTTPStatus.OK:
            raise SystemExit(
                f'Error: Received status code != 200 ({response.status_code})'
            )
        
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        scripts = soup.find_all('script')

        json_text = scripts[-1].text
        json_data = json.loads(json_text)

        pagination = (
            json_data['props']['pageProps']['data']
            ['searchAds']['pagination']
        )

        total_pages = int(pagination['totalPages'])

        return total_pages


    async def fetch_all(self, total_pages: int) -> list[Response]:
        params_list = [
            {'limit': 72, 'page': page} for page in range(2, total_pages + 1)
        ]

        transport = AsyncHTTPTransport(retries=3)
        async with AsyncClient(
            follow_redirects=True, timeout=15, transport=transport
        ) as client:
            tasks = [
                client.get(url=self.url, params=params, headers=self.headers) 
                for params in params_list
            ]
            responses = await asyncio.gather(*tasks)
            return responses
    
    def extract_ads(self, responses: list[Response]) -> list[dict]:
        # Add logging here to capture responses with status codes other than 200
        list_ads: list = []
        for response in responses:
            if response.status_code == HTTPStatus.OK:
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')
                scripts = soup.find_all('script')
                json_data = json.loads(scripts[-1].text)
                list_ads = json_data['props']['pageProps']['data']['searchAds']['items']
                list_ads_promoted = json_data['props']['pageProps']['data']['searchAdsRandomPromoted']['items']
                list_ads.extend(list_ads)
                list_ads.extend(list_ads_promoted)
        
        return list_ads

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