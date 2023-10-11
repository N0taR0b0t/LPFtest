import json

def check_json_syntax(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data = file.read()

    # Try using the json parser for primary validation
    try:
        json.loads(data)
        print("No syntax errors found!")
        return
    except json.JSONDecodeError as e:
        # If the parser catches errors, let's do deeper inspections for better error messages
        print(f"Error detected by the parser: {e}")
    
    stack = []
    line_number = 1
    column_number = 0
    double_quote_count = 0
    last_double_quote_position = None
    errors = []

    for char in data:
        column_number += 1

        if char == '\n':
            line_number += 1
            column_number = 0

        # Count and track quotes
        if char == "'":
            errors.append(f"Invalid single quote at line {line_number}, column {column_number}. JSON keys and values should be wrapped in double quotes.")
        elif char == '"':
            double_quote_count += 1
            last_double_quote_position = (line_number, column_number)

        # For symbols that can have an opening and closing
        if char in ['{', '[']:
            stack.append((char, line_number, column_number))
        elif char in ['}', ']']:
            if not stack:
                errors.append(f"Unmatched {char} at line {line_number}, column {column_number}")
                continue
            last_open, last_line, last_column = stack.pop()
            if char == '}' and last_open != '{':
                errors.append(f"Mismatched {char} for {last_open} from line {last_line}, column {last_column} at line {line_number}, column {column_number}")
                continue
            elif char == ']' and last_open != '[':
                errors.append(f"Mismatched {char} for {last_open} from line {last_line}, column {last_column} at line {line_number}, column {column_number}")
                continue

    # Check for unmatched opening characters after scanning the whole file
    while stack:
        last_open, last_line, last_column = stack.pop()
        errors.append(f"Unmatched {last_open} at line {last_line}, column {last_column}")

    if double_quote_count % 2 != 0 and last_double_quote_position:
        errors.append(f"Unmatched double quote at line {last_double_quote_position[0]}, column {last_double_quote_position[1]}")

    # Display results
    if errors:
        for error in errors:
            print(error)

if __name__ == '__main__':
    check_json_syntax('linked_places_output.json')
