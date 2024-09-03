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


def extract_data(
    mongo_conn: MongoConnection, collection_name: str
) -> list[dict]:
    data = mongo_conn.get_data_from_collection(
        collection=collection_name, fields=FIELDS
    )

    return data


def transform_data(data: list[dict]) -> list[dict]:
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

    transformed_data = transform_data(data=data)

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
