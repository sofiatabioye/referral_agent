import json

def clean_and_parse_json(raw_response):
    """
    Cleans and parses a raw response to extract valid JSON.
    Args:
        raw_response (str): The raw text containing JSON.

    Returns:
        dict: Parsed JSON as a Python dictionary.

    Raises:
        ValueError: If the JSON cannot be extracted or parsed.
    """
    try:
        # Find the first '{' and last '}' to locate the JSON boundaries
        json_start = raw_response.index('{')
        json_end = raw_response.rindex('}') + 1  # Include the last '}'

        # Extract the JSON segment
        clean_json = raw_response[json_start:json_end]
        
        # Parse the JSON
        parsed_data = json.loads(clean_json)
        return parsed_data
    except (ValueError, json.JSONDecodeError) as e:
        raise ValueError(f"Failed to clean or parse JSON: {e}")
