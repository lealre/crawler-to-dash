import re

import pandas as pd

from src.cleaners.default_cleaner import AbstractCleaner


class SapoCleaner(AbstractCleaner):
    def __init__(self) -> None:
        super().__init__(collection='raw_sapo')

    def clean_data(self):

        self.get_collection_dataframe()

        self.splitting_location()
        self.splitting_info_agg()

        self.clean_property_status_and_area()
        self.clean_num_bedrooms()
        self.clean_change_columns_and_data_types()

        self.drop_columns_and_duplicated()

        self.set_unique_id()

        self.reindex_dataframe()

        return self.df

    def splitting_location(self):
        df_location_info_splitted = (
            self.df['location']
            .str.split(',', expand=True)
        )
        df_location_info_splitted.columns = [
            f'location_zone_{n}' for n in df_location_info_splitted.columns
        ]
        self.df = self.df.join(df_location_info_splitted)

    def splitting_info_agg(self):
        df_info_agg_splitted = (
            self.df['info_agg']
            .str.split('·',
            expand=True)
        )
        df_info_agg_splitted.columns = [
            f'info_{n}' for n in df_info_agg_splitted.columns
        ]
        self.df = self.df.join(df_info_agg_splitted)

        self.df.rename(
            columns={
                'info_0': 'property_status',
                'info_1': 'area_m2',
            },
            inplace=True
        )

    def clean_property_status_and_area(self):
        self.df = self.df.apply(
            self.apply_correct_area_and_property_status_values, axis=1
        )

        self.df['property_status'] = (
            self.df['property_status']
            .str.strip()
            .replace('', None)
        )

        self.df['area_m2'] = (
            self.df['area_m2'].str.replace(r'\D', '', regex=True)
        )
        self.df['area_m2'] = (
            pd.to_numeric(self.df['area_m2'], errors='coerce')
        )

    def clean_num_bedrooms(self):
        pattern_num_bedrooms = r'(T\d\S*)'
        self.df['num_bedrooms'] = (
            self.df['type'].str.extract(pattern_num_bedrooms)
        )

        self.df['num_bedrooms'] = self.df['num_bedrooms'].apply(
            self.apply_sum_num_bedrooms
        )

        self.df['num_bedrooms'] = self.df['num_bedrooms'].apply(
            self.apply_normalize_num_bedrooms
        )

    def clean_change_columns_and_data_types(self):
        self.df.rename(
            columns={
                'type': 'title',
            },
            inplace=True
        )

        self.df['date_extracted'] = (
            pd.to_datetime(self.df['date_extracted']).dt.date
        )

        self.df['price_euro'] = (
            self.df['price_euro'].str.replace(r'\D', '', regex=True)
        )
        self.df['price_euro'] = (
            pd.to_numeric(self.df['price_euro'], errors='coerce')
        )

        self.df['sub_location_search'] = (
            self.df['sub_location_search']
            .apply(lambda x: None if not x else x)
        )

    def drop_columns_and_duplicated(self):
        self.df = self.df.drop(
            columns=['location', 'info_agg']
        )

        self.df.drop_duplicates(inplace=True)

    def set_unique_id(self):
        index_to_remove = self.df[
            (self.df.link.duplicated(keep='first'))
            & (self.df.offer_type_search == 'alugar')
        ].index

        self.df.drop(index=index_to_remove, inplace=True)

        pattern = r'([a-zA-Z0-9\-]{32})\.html$'
        self.df['link_id'] = self.df['link'].str.extract(pattern)
        self.df['link_id'] = self.df['link_id'].astype(str)
        self.df['link_id'] = self.df['link_id'].replace('nan', None)

    @staticmethod
    def apply_correct_area_and_property_status_values(row):
        pattern_has_number = r'\d'
        if (
            re.match(pattern_has_number, row['property_status'])
        ):
            row['area_m2'] = row['property_status']
            row['property_status'] = None
        return row

    @staticmethod
    def apply_sum_num_bedrooms(record):
        record_len = 4
        if (
            isinstance(record, str)
            and '+' in record
            and len(record) == record_len
        ):
            begin_str, end_str = record.split('+')
            real_sum = int(end_str) + int(begin_str[-1])
            return f'T{real_sum}'
        return record

    @staticmethod
    def apply_normalize_num_bedrooms(record):
        values_accepted = [f'T{n}' for n in range(10)]
        values_accepted.append('T9+')
        if (
            isinstance(record, str)
            and record not in values_accepted
        ):
            return 'T9+'
        return record
