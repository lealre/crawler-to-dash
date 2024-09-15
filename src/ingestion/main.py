"""
From crawling the data, consolidating it, and transforming it for use in the
Dashboard, all within MongoDB.

Crawl Data -> Consolidate Data -> Create Dashboard Collection
"""

from src.core.mongodb import MongoConnection
from src.core.settings import settings
from src.ingestion.consolidate import Consolidate
from src.ingestion.crawler.imovirtual_crawler import ImovirtualCrawler
from src.ingestion.dash_etl import dash_pipeline

offer_types_search = ['arrendar', 'comprar']
property_types_search = ['apartamento', 'moradia']
location_search = ['lisboa']
sub_location_search = ['']

raw_collection = settings.COLLECTION_RAW
consolidated_collection = settings.COLLECTION_CONSOLIDATE
dash_collection = settings.COLLECTION_DASH

mongo = MongoConnection()

ImovirtualCrawler().crawl(
    offer_types=offer_types_search,
    property_types=property_types_search,
    locations=location_search,
    sub_locations=sub_location_search,
)

Consolidate(raw_collection='raw_imovirtual').consolidate()


dash_pipeline(
    mongo_conn=mongo,
    extract_from=consolidated_collection,
    load_to=dash_collection,
)
