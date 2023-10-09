import pandas as pd
from shapely import wkb, ops
from pydantic import BaseModel
import json
import pyproj
import warnings

# Schema Representation
class GeoJSON_T(BaseModel):
    type: str
    geometry: dict
    properties: dict
    when: dict

class LinkedPlaces(BaseModel):
    type: str
    properties: dict
    geometry: dict
    when: dict

# Parsing Geometry Data
def parse_geom(hex_str):
    return wkb.loads(bytes.fromhex(hex_str), hex=True)

# New function to perform the CRS transformation
def transform_geom(geometry):
    project = pyproj.Transformer.from_proj(
        pyproj.Proj('epsg:3587'),
        pyproj.Proj('epsg:4326'),  # to standard lat/long
        always_xy=True
    ).transform
    return ops.transform(project, geometry)

# Data Ingestion
def ingest_data(data):
    geojson_t_data = []
    linked_places_data = []

    for index, row in data.iterrows():
        row = row.fillna("")  # replace NaN values with empty strings
        geojson_t_item = GeoJSON_T(
            type="Feature",
            geometry=row['geometry'].__geo_interface__,
            properties=row.drop('geometry').to_dict(),
            when={"start": row['year']}
        )
        linked_places_item = LinkedPlaces(
            type="Feature",
            geometry=row['geometry'].__geo_interface__,
            properties=row.drop('geometry').to_dict(),
            when={"start": row['year']}
        )
        geojson_t_data.append(geojson_t_item.dict())
        linked_places_data.append(linked_places_item.model_dump())  # updated method

    return geojson_t_data, linked_places_data

def main():
    # Set up warnings handling
    warnings.simplefilter("always")  # Change to always to count all instances of warnings
    with warnings.catch_warnings(record=True) as w:
        # Data Reading
        data = pd.read_csv('data_output.csv')
        data['geometry'] = data['geom'].apply(parse_geom).apply(transform_geom)  # modified this line

        # Data Ingestion
        geojson_t_data, linked_places_data = ingest_data(data)

        # Output to JSON files
        with open('geojson_t_output.json', 'w') as f:
            json.dump(geojson_t_data, f, indent=2)

        with open('linked_places_output.json', 'w') as f:
            json.dump(linked_places_data, f, indent=2)

        # After processing, display the count of additional warnings if more than 10
        if len(w) > 10:
            print(f"Done Processing with {len(w) - 10} additional warnings.")

if __name__ == "__main__":
    main()
