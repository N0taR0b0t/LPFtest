import json

def validate_lpf(json_data):
    violations = []
    
    if "type" not in json_data or json_data["type"] != "FeatureCollection":
        violations.append("Root 'type' must be 'FeatureCollection'")
    
    if "@context" not in json_data:
        violations.append("'@context' is required.")
    
    if "features" not in json_data:
        violations.append("'features' element is missing.")
    else:
        for feature in json_data["features"]:
            if "@id" not in feature:
                violations.append("Feature missing '@id'.")
            if "type" not in feature or feature["type"] != "Feature":
                violations.append("Feature 'type' must be 'Feature'.")
            if "properties" not in feature:
                violations.append("Feature missing 'properties'.")
            else:
                if "title" not in feature["properties"]:
                    violations.append("Properties missing 'title'.")
                if "ccodes" in feature["properties"]:
                    if not isinstance(feature["properties"]["ccodes"], list):
                        violations.append("'ccodes' should be a list.")
            if "when" not in feature:
                violations.append("Feature missing 'when'.")
            else:
                if "timespans" not in feature["when"]:
                    violations.append("'when' missing 'timespans'.")
            if "geometry" not in feature:
                violations.append("Feature missing 'geometry'.")
            if "names" not in feature:
                violations.append("Feature missing 'names'.")
            else:
                if not any("citations" in name for name in feature["names"]):
                    violations.append("At least one name must have a citation.")
    
    return violations

with open("linked_places_output.json", "r") as file:
    data = json.load(file)
    issues = validate_lpf(data)
    
    if issues:
        print("Found violations:")
        for issue in issues:
            print("-", issue)
    else:
        print("No violations found.")


