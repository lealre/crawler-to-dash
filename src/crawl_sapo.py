import sys
import os
# Add the root directory of your project to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.crawlers.sapo_crawler import SapoCrawler


offer_types_search = [
    # 'comprar', 
    'alugar']
property_types_search = [
    # 'apartamentos', 
    'moradias'
]
location_search = [
    'mafra'
    # 'distrito.lisboa'
]
sub_location_search = ['']

SapoCrawler().crawl(
    offer_types=offer_types_search,
    property_types=property_types_search,
    locations=location_search,
    sub_locations=sub_location_search,
)