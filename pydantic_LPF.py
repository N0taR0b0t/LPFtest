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
    geojson_t_data = []
    linked_places_data = []

    for index, row in data.iterrows():
        row = row.fillna("")  # replace NaN values with empty strings
        
        # Constructing the names array
        names = []
        if row['sname_o']:
            names.append({"toponym": row['sname_o']})
        if row['lname_o']:
            names.append({"toponym": row['lname_o']})
        if row['variants_o']:
            names.extend([{"toponym": name.strip()} for name in row['variants_o'].split(",")])
        if row['sname_h']:
            names.append({"toponym": row['sname_h']})
        if row['lname_h']:
            names.append({"toponym": row['lname_h']})
        if row['variants_h']:
            names.extend([{"toponym": name.strip()} for name in row['variants_h'].split(",")])
        
        properties = {
            "title": row['short_name'],
            **row.drop(['geometry', 'geom', 'year', 'short_name', 'sname_o', 'lname_o', 'variants_o', 'sname_h', 'lname_h', 'variants_h']).to_dict()
        }
        
        geojson_t_item = {
            "@id": str(row['id']),
            "type": "Feature",
            "geometry": row['geometry'].__geo_interface__,
            "properties": properties,
            "names": names,
            "when": {"timespans": [{"start": {"in": str(row['year'])}}]}
        }
        
        linked_places_item = {
            "@id": str(row['id']),
            "type": "Feature",
            "geometry": row['geometry'].__geo_interface__,
            "properties": properties,
            "names": names,
            "when": {"timespans": [{"start": {"in": str(row['year'])}}]}
        }
        
        geojson_t_data.append(geojson_t_item)
        linked_places_data.append(linked_places_item)

    return geojson_t_data, linked_places_data

def main():
    # Set up warnings handling
    warnings.simplefilter("always")  # Change to always to count all instances of warnings
    with warnings.catch_warnings(record=True) as w:
        # Data Reading
        data = pd.read_csv('data_output.csv')
        data['geometry'] = data['geom'].apply(parse_geom).apply(transform_geom)  # modified this line

        # Data Ingestion
        geojson_t_features, linked_places_features = ingest_data(data)

        geojson_t_data = {
            "@context": "http://linkedpasts.org/assets/linkedplaces-context-v1.jsonld",
            "type": "FeatureCollection",
            "features": geojson_t_features
        }

        linked_places_data = {
            "@context": "http://linkedpasts.org/assets/linkedplaces-context-v1.jsonld",
            "type": "FeatureCollection",
            "features": linked_places_features
        }

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
