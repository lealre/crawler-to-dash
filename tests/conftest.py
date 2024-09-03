import pytest


@pytest.fixture
def raw_data():
    raw_data = [
        {'id': number, 'field': f'field_{number}'} for number in range(1, 11)
    ]

    return raw_data


@pytest.fixture
def filtered_data():
    filtered_data = [
        {'id': number, 'field': f'field_{number}', 'is_available': True}
        for number in range(1, 11)
    ]

    return filtered_data


@pytest.fixture
def consolidated_data():
    consolidated_data = [
        {
            'id': number,
            'field': f'field_{number}',
            'is_available': (number % 2 == 0),
        }
        for number in range(6, 16)
    ]

    return consolidated_data
