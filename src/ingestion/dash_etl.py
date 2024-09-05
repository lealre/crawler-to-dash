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
    'MORE': 'T9+'
}


def extract_data(
    mongo_conn: MongoConnection, collection_name: str
) -> list[dict]:
    if not mongo_conn.ping():
        raise SystemExit()

    data = mongo_conn.get_data_from_collection(
        collection=collection_name, fields=FIELDS
    )

    return data


def filter_data(data: list[dict]) -> list[dict]:
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
    mongo_conn.save_data(
        collection=collection_name, data=data, unique_index=UNIQUE_INDEX
    )


def dash_pipeline(
    mongo_conn: MongoConnection, extract_from: str, load_to: str
) -> None:
    data = extract_data(mongo_conn=mongo_conn, collection_name=extract_from)

    filtered_data = filter_data(data=data)

    transformed_data = transform_data(data=filtered_data)

    load_data(
        mongo_conn=mongo_conn, collection_name=load_to, data=transformed_data
    )


if __name__ == '__main__':
    consolidated_collection = 'consolidated_imovirtual'
    dash_collection = 'dash'

    mongo = MongoConnection()

    dash_pipeline(
        mongo_conn=mongo,
        extract_from=consolidated_collection,
        load_to=dash_collection,
    )
