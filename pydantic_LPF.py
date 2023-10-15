import pandas as pd
from shapely import wkb, ops
import json
import pyproj
import warnings

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
    linked_places_data = []

    default_citation = [{"url": "https://euratlas.com"}]  # Default citation

    for index, row in data.iterrows():
        row = row.fillna("")  # replace NaN values with empty strings

        # Constructing the names array
        names = []
        for toponym_field in ['sname_o', 'lname_o', 'variants_o', 'sname_h', 'lname_h', 'variants_h']:
            if row[toponym_field]:
                toponyms = [row[toponym_field]] if 'variants' not in toponym_field else row[toponym_field].split(',')
                names.extend([{"toponym": name.strip(), "citations": default_citation} for name in toponyms])

        properties = {
            "title": row['short_name'],
            **row.drop(['geometry', 'geom', 'year', 'short_name', 'sname_o', 'lname_o', 'variants_o', 'sname_h', 'lname_h', 'variants_h']).to_dict()
        }

        linked_places_item = {
            "@id": str(row['id']),
            "type": "Feature",
            "geometry": row['geometry'].__geo_interface__,
            "properties": properties,
            "names": names,
            "when": {"timespans": [{"start": {"in": str(row['year'])}}]}
        }

        linked_places_data.append(linked_places_item)

    return linked_places_data

def main():
    # Set up warnings handling
    warnings.simplefilter("always")  # Change to always to count all instances of warnings
    with warnings.catch_warnings(record=True) as w:
        # Data Reading
        data = pd.read_csv('data_output.csv')
        data['geometry'] = data['geom'].apply(parse_geom).apply(transform_geom)  # modified this line

        # Data Ingestion
        linked_places_features = ingest_data(data)

        linked_places_data = {
            "@context": "http://linkedpasts.org/assets/linkedplaces-context-v1.jsonld",
            "type": "FeatureCollection",
            "features": linked_places_features
        }

        # Output to JSON file
        with open('linked_places_output.json', 'w') as f:
            json.dump(linked_places_data, f, indent=2)

        # After processing, display the count of additional warnings if more than 10
        if len(w) > 10:
            print(f"Done Processing with {len(w) - 10} additional warnings.")

if __name__ == "__main__":
    main()
