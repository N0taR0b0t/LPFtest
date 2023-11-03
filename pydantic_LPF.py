import pandas as pd
from shapely import wkb, ops
from shapely.geometry import LineString, Point, Polygon, MultiLineString
from shapely.geometry import MultiPolygon
import json
import pyproj
import warnings
import string

from shapely.geometry import Point, LineString, Polygon, MultiPolygon

def delete_every_other_point(geometry):
    if isinstance(geometry, Point):
        # A point cannot have "every other point" removed; it is returned as-is.
        return geometry

    elif isinstance(geometry, LineString):
        # Create a new LineString with every other point from the original.
        new_coords = [coord for i, coord in enumerate(geometry.coords) if i % 2 == 0]
        if len(new_coords) < 2:
            # A valid LineString requires at least two points.
            # Handle this case appropriately.
            raise ValueError("LineString has too few points after deletion.")
        return LineString(new_coords)

    elif isinstance(geometry, Polygon):
        # Handle the exterior ring
        exterior_coords = [coord for i, coord in enumerate(geometry.exterior.coords) if i % 2 == 0]
        if len(exterior_coords) < 3:
            # A valid Polygon requires at least three points in the exterior ring.
            # Handle this case appropriately.
            raise ValueError("Polygon has too few points in the exterior ring after deletion.")

        # Handle the interior rings (holes)
        new_interiors = []
        for interior in geometry.interiors:
            interior_coords = [coord for i, coord in enumerate(interior.coords) if i % 2 == 0]
            if len(interior_coords) >= 3:
                new_interiors.append(interior_coords)
            # If an interior ring has fewer than 3 points, it will be discarded.

        return Polygon(exterior_coords, new_interiors)

    elif isinstance(geometry, MultiPolygon):
        new_polygons = []
        for polygon in geometry.geoms:
            new_exterior_coords = [coord for i, coord in enumerate(polygon.exterior.coords) if i % 2 == 0]
            if len(new_exterior_coords) < 3:
                # Handle invalid exteriors appropriately; here they are skipped.
                continue

            new_interiors = []
            for interior in polygon.interiors:
                new_interior_coords = [coord for i, coord in enumerate(interior.coords) if i % 2 == 0]
                if len(new_interior_coords) >= 3:
                    new_interiors.append(new_interior_coords)
                # Interior rings with fewer than 3 points will be discarded.

            new_polygons.append(Polygon(new_exterior_coords, new_interiors))
        return MultiPolygon(new_polygons)

    else:
        raise ValueError(f"Geometry type '{type(geometry)}' not supported")

# Parsing Geometry Data
def parse_geom(hex_str):
    return wkb.loads(bytes.fromhex(hex_str), hex=True)

# New function to perform the CRS transformation
def transform_geom(geometry):
    project = pyproj.Transformer.from_proj(
        pyproj.Proj('epsg:3857'),
        pyproj.Proj('epsg:4326'),  # to standard lat/long
        always_xy=True
    ).transform
    return ops.transform(project, geometry)

# Data Ingestion
def ingest_data(data):
    linked_places_data = []

    for index, row in data.iterrows():
        row = row.fillna("")  # replace NaN values with empty strings

        # Constructing the names array
        names = []
        for name_key in ['short_name', 'sname_o', 'variants_o', 'sname_h', 'lname_h', 'variants_h']:
            if row[name_key]:
                for name in row[name_key].split(","):
                    name = name.strip()
                    name_entry = {"toponym": name, "citations": [{"label": "Euratlas Polities"}]}
                    names.append(name_entry)


        properties = {
            "title": row['lname_o'],
            **row.drop(['geometry', 'geom', 'year', 'short_name', 'sname_o', 'lname_o', 'variants_o', 'sname_h', 'lname_h', 'variants_h']).to_dict()
        }
        row['geometry'] = delete_every_other_point(row['geometry'])

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
        data = pd.read_csv('data_output.csv', encoding='utf-8')
        data['geometry'] = data['geom'].apply(parse_geom).apply(transform_geom)  # modified this line

        # Data Ingestion
        linked_places_features = ingest_data(data)

        linked_places_data = {
            "@context": "http://linkedpasts.org/assets/linkedplaces-context-v1.jsonld",
            "type": "FeatureCollection",
            "features": linked_places_features
        }

        # Output to JSON file
        with open('linked_places_output.json', 'w', encoding='utf-8') as f:
            json.dump(linked_places_data, f, indent=2, ensure_ascii=False)

        # After processing, display the count of additional warnings if more than 10
        if len(w) > 10:
            print(f"Done Processing with {len(w) - 10} additional warnings.")

if __name__ == "__main__":
    main()
