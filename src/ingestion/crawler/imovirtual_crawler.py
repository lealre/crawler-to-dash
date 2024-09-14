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
    - List of items:
    json_data['props']['pageProps']['data']['searchAds']['items']
    - Promoted items:
    json_data['props']['pageProps']['data']['searchAdsRandomPromoted']['items']
    - Pagination:
    json_data['props']['pageProps']['data']['searchAds']['pagination']
"""

import asyncio
import itertools
import json
from http import HTTPStatus

import requests
from bs4 import BeautifulSoup
from httpx import AsyncClient, AsyncHTTPTransport
from requests.models import Response

from src.ingestion.crawler.default_crawler import AbstractCrawler


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
    ) -> None:
        '''
        Crawl the site to extract data based on various combinations
        of offer types, property types, locations, and sub-locations.

        Args:
            offer_types (list[str]): List of offer types to query.
            property_types (list[str]): List of property types to query.
            locations (list[str]): List of locations to query.
            sub_locations (list[str]): List of sub-locations to query.

        This method generates all possible combinations of the provided
        parameters, constructs the query URL, fetches the data
        asynchronously, and saves the extracted ads based on the settings.
        '''

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

            print(f' -- Query Search: {offer_type}, {property_type} -- ')

            self.url = (
                f'{self.base_url}{offer_type}/' f'{property_type}/{location}'
            )

            if sub_location:
                self.url = f'{self.url}/{sub_location}'

            total_pages = self.get_number_of_pages()
            responses = asyncio.run(self.fetch_all(total_pages=total_pages))
            list_ads = self.extract_ads(responses=responses)

            print(f'Ads extracted: {len(list_ads)}')

            self.data.extend(list_ads)

        print(f'{20 * '-'}\nTotal Ads extracted: {len(self.data)}')

        if self.local_storage:
            self.save_json_locally()

        if self.mongo_storage:
            self.save_json_to_mongodb()

        if self.aws_s3_storage:
            self.save_json_to_s3()

    def get_number_of_pages(self) -> int:
        '''
        Retrieve the total number of pages available for the current
        URL query combination, so it can be used as a parameter in
        further asynchronous requests.

        Returns:
            int: The total number of pages for the current query.

        Raises:
            SystemExit: If the HTTP response status code is not 200 (OK).
        '''

        response = requests.get(
            self.url, params=self.params, headers=self.headers
        )
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
            json_data.get('props', {})
            .get('pageProps', {})
            .get('data', {})
            .get('searchAds', {})
            .get('pagination')
        )

        total_pages = int(pagination['totalPages'])
        total_results = int(pagination['totalResults'])

        print(f'Total results found: {total_results}')
        print(f'Total pages: {total_pages}')

        return total_pages

    async def fetch_all(self, total_pages: int) -> list[Response]:
        '''
        Asynchronously fetch all pages for the URL query combination.

        Args:
            total_pages (int): The total number of pages to fetch.

        Returns:
            list[Response]: A list of HTTP responses for each page.

        This method creates asynchronous HTTP requests for all pages
        and returns the list of responses.
        '''

        print('Starting async requests...')

        params_list = [
            {'limit': 72, 'page': page} for page in range(1, total_pages + 1)
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

        print('All requests have been completed!')
        return responses

    @staticmethod
    def extract_ads(responses: list[Response]) -> list[dict]:
        '''
        Extracts advertisements from a list of HTTP responses.

        This method processes each response, parsing the HTML content to
        find and extract advertisement data from JSON embedded in the
        script tags. It handles both regular and promoted ads,
        combining them into a single list.

        Args:
            responses (list[Response]):
            A list of HTTP response objects containing the page data.

        Returns:
            list[dict]: A list of dictionaries, each representing an
            advertisement. The list includes both regular and promoted
            ads extracted from the responses.

        Notes:
            - This method assumes that the JSON data containing ads is
            embedded in the last <script> tag of the HTML content.
            - The extraction relies on the presence of specific JSON
            structure in the page data.
        '''

        print('Data extraction started..')

        all_ads: list = []
        for response in responses:

            if response.status_code == HTTPStatus.OK:
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')

                scripts = soup.find_all('script')
                json_data = json.loads(scripts[-1].text)

                data = (
                    json_data
                    .get('props', {})
                    .get('pageProps', {})
                    .get('data', {})
                )
                list_ads = data.get('searchAds', {}).get('items', [])
                list_ads_promoted = (
                    data.get('searchAdsRandomPromoted', {}).get('items', [])
                )

                all_ads.extend(list_ads)
                all_ads.extend(list_ads_promoted)

                print(
                    f'{len(list_ads) + len(list_ads_promoted)} '
                    f'ads extracted from {response.url}'
                )

        return all_ads


if __name__ == '__main__':
    offer_types_search = ['arrendar', 'comprar']
    property_types_search = ['apartamento', 'moradia']
    location_search = ['lisboa']
    sub_location_search = ['']

    ImovirtualCrawler().crawl(
        offer_types=offer_types_search,
        property_types=property_types_search,
        locations=location_search,
        sub_locations=sub_location_search,
    )
