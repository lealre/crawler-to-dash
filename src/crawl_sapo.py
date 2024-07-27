from src.crawlers.sapo_crawler import SapoCrawler

offer_types_search = [
    # 'comprar',
    'alugar'
]
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
