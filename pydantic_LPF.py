import pandas as pd
from shapely import wkb
from pydantic import BaseModel
import json

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

# Data Ingestion
def ingest_data(data):
    geojson_t_data = []
    linked_places_data = []

    for index, row in data.iterrows():
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
        linked_places_data.append(linked_places_item.dict())

    return geojson_t_data, linked_places_data

def main():
    # Data Reading
    data = pd.read_csv('data_output.csv')
    data['geometry'] = data['geom'].apply(parse_geom)
    
    # Data Ingestion
    geojson_t_data, linked_places_data = ingest_data(data)

    # Output to JSON files
    with open('geojson_t_output.json', 'w') as f:
        json.dump(geojson_t_data, f, indent=2)

    with open('linked_places_output.json', 'w') as f:
        json.dump(linked_places_data, f, indent=2)

    print("Done Processing")

if __name__ == "__main__":
    main()
