import pandas as pd

from src.core.mongodb import MongoConnection

FIELDS = [
    'id',
    'title',
    'estate',
    'transaction',
    'location.address.city.name',
    'location.reverseGeocoding.locations',
    'totalPrice.value',
    'pricePerSquareMeter.value',
    'areaInSquareMeters',
    'roomsNumber',
]

UNIQUE_INDEX = 'id'

VALUES_TO_MAP = {
    'ONE': 'T0',
    'TWO': 'T1',
    'THREE': 'T2',
    'FOUR': 'T3',
    'FIVE': 'T4',
    'SIX': 'T5',
    'SEVEN': 'T6',
    'EIGHT': 'T7',
    'NINE': 'T8',
    'TEN': 'T9',
    'MORE': 'T9+',
}


def extract_data(
    mongo_conn: MongoConnection, collection_name: str
) -> list[dict]:
    '''
    Extracts data from a MongoDB collection.

    Parameters:
    ----------
    mongo_conn : MongoConnection
        An active MongoDB connection.
    collection_name : str
        The name of the MongoDB collection to extract data from.

    Returns:
    -------
    list[dict]
        A list of documents (as dictionaries) retrieved from the specified
        collection.

    Raises:
    -------
    SystemExit
        If the MongoDB connection cannot be established.
    '''

    if not mongo_conn.ping():
        raise SystemExit()

    data = mongo_conn.get_data_from_collection(
        collection=collection_name, fields=FIELDS
    )

    return data


def filter_data(data: list[dict]) -> list[dict]:
    '''
    Filters and restructures the data by extracting relevant fields such as
    location, price per square meter, and total price. Adds the city
    information to the documents.

    Parameters:
    ----------
    data : list[dict]
        A list of documents (as dictionaries) to be filtered.

    Returns:
    -------
    list[dict]
        A list of filtered and updated documents.
    '''

    for item in data:
        location = (
            item.get('location', {})
            .get('reverseGeocoding', {})
            .get('locations')
        )
        if isinstance(location, list):
            location = location[1].get('id')

        price_square_meter = item.get('pricePerSquareMeter', {}).get('value')
        total_price = item.get('totalPrice', {}).get('value')
        city = (
            item.get('location', {})
            .get('address', {})
            .get('city', {})
            .get('name')
        )

        update = {
            'location': location,
            'pricePerSquareMeter': price_square_meter,
            'totalPrice': total_price,
        }

        item.update(update)
        item['city'] = city

    return data


def transform_data(data: list[dict]) -> list[dict]:
    '''
    Transforms the filtered data by cleaning, mapping values, and
    restructuring location information to a consistent format.
    Filters the data to only include entries from Lisbon.

    Parameters:
    ----------
    data : list[dict]
        A list of filtered documents (as dictionaries) to be transformed.

    Returns:
    -------
    list[dict]
        A list of transformed documents ready for loading into MongoDB.
    '''

    df = pd.DataFrame(data)

    df.dropna(inplace=True)

    df['roomsNumberNotation'] = df['roomsNumber'].map(VALUES_TO_MAP)

    df = df[df.location.str.startswith('lisboa/')]

    df['location'] = (
        df['location']
        .str.replace('lisboa/', '')
        .str.replace('-', ' ')
        .str.title()
    )

    return df.to_dict(orient='records')


def load_data(
    mongo_conn: MongoConnection, data: list[dict], collection_name: str
) -> None:
    '''
    Loads the transformed data into a specified MongoDB collection.

    Parameters:
    ----------
    mongo_conn : MongoConnection
        An active MongoDB connection.
    data : list[dict]
        A list of documents (as dictionaries) to be loaded.
    collection_name : str
        The name of the MongoDB collection to load data into.
    '''

    mongo_conn.save_data(
        collection=collection_name, data=data, unique_index=UNIQUE_INDEX
    )


def dash_pipeline(
    mongo_conn: MongoConnection, extract_from: str, load_to: str
) -> None:
    '''
    Orchestrates the end-to-end pipeline of extracting, filtering,
    transforming, and loading data into MongoDB for a dashboard.

    Parameters:
    ----------
    mongo_conn : MongoConnection
        An active MongoDB connection.
    extract_from : str
        The name of the MongoDB collection to extract data from.
    load_to : str
        The name of the MongoDB collection to load transformed data into.
    '''

    data = extract_data(mongo_conn=mongo_conn, collection_name=extract_from)

    filtered_data = filter_data(data=data)

    transformed_data = transform_data(data=filtered_data)

    load_data(
        mongo_conn=mongo_conn, collection_name=load_to, data=transformed_data
    )


if __name__ == '__main__':

    from src.core.settings import settings
    consolidated_collection = settings.COLLECTION_CONSOLIDATE
    dash_collection = settings.COLLECTION_DASH

    mongo = MongoConnection()

    dash_pipeline(
        mongo_conn=mongo,
        extract_from=consolidated_collection,
        load_to=dash_collection,
    )
