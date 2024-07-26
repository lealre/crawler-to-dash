import sys
import os
# Add the root directory of your project to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.crawlers.imovirtual_crawler import ImovirtualCrawler


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