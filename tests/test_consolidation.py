from typing import Any

from src.consolidate import Consolidate


def test_filter_unique_and_add_availability(raw_data: list[dict]):
    expected_length = 10

    raw_data.append({'id': 1, 'field': 'filed_1'})
    raw_data.append({'id': 2, 'field': 'filed_2'})

    filtered_data = Consolidate.filter_unique_and_add_availability(
        data=raw_data
    )

    assert len(filtered_data) == expected_length
    assert all(item.get('is_available') for item in filtered_data)


def test_update_availability(
    filtered_data: list[dict[str, Any]],
    consolidated_data: list[dict[str, Any]],
):
    expected_lenth = 2

    ids_to_update = Consolidate.update_availability(
        consolidated_data=consolidated_data, filtered_data=filtered_data
    )

    assert len(ids_to_update) == expected_lenth


def test_insert_new_ads(
    filtered_data: list[dict[str, Any]],
    consolidated_data: list[dict[str, Any]],
):
    expected_length = 5
    consolidated_ids = [item.get('id') for item in consolidated_data]

    new_ads = Consolidate.insert_new_ads(
        consolidated_data=consolidated_data, filtered_data=filtered_data
    )

    assert len(new_ads) == expected_length
    assert all(
        item.get('id')
        for item in new_ads
        if item.get('id') not in consolidated_ids
    )
