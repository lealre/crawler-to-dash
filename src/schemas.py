import pandera as pa
from pandera.typing import Series

values_accepted = [f'T{n}' for n in range(10)]
values_accepted.append('T9+')


class StageSchema(pa.DataFrameModel):
    title: Series[str] = pa.Field(nullable=True)
    price_euro: Series[float] = pa.Field(nullable=True)
    area_m2: Series[float] = pa.Field(nullable=True)
    num_bedrooms: Series[str] = pa.Field(
        isin=values_accepted, nullable=True
    )
    property_status: Series[str] = pa.Field(nullable=True)
    location_zone_0: Series[str] = pa.Field(nullable=True)
    location_zone_1: Series[str] = pa.Field(nullable=True)
    location_zone_2: Series[str] = pa.Field(nullable=True)
    location_zone_3: Series[str] = pa.Field(nullable=True)
    location_zone_4: Series[str] = pa.Field(nullable=True)
    location_zone_5: Series[str] = pa.Field(nullable=True)
    location_zone_6: Series[str] = pa.Field(nullable=True) 
    site: Series[str] = pa.Field(isin = ['sapo'], nullable=True) 
    link_id: Series[str] = pa.Field(nullable=True)
    link: Series[str] = pa.Field(nullable= False, unique = True)
    offer_type_search: Series[str] = pa.Field(nullable=True)
    property_type_search: Series[str] = pa.Field(nullable=True)
    location_search: Series[str] = pa.Field(nullable=True)
    sub_location_search: Series[str] = pa.Field(nullable=True)
    date_extracted: Series[pa.DateTime] = pa.Field(nullable=False) 

    class Config:
        strict = True
        coerce = True