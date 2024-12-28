def map_json_to_conditions(parsed_json):
    """
    Maps JSON summary data to Neo4j-compatible conditions.
    Args:
        parsed_json (dict): The JSON-structured summary of patient data.

    Returns:
        list: A list of conditions mapped to the Neo4j database.
    """
    # Define the mappings for JSON keys to Neo4j condition names
    condition_mappings = {
        "Patient is 40 years old or older": "Patient is 40 years old or older",
        "Patient is 50 years old or older": "Patient is 50 years old or older",
        "Patient is less than 50 years old": "Patient is less than 50 years old",
        "Rectal bleeding": "Rectal bleeding",
        "Change in bowel habit": "Change in bowel habit",
        "Weight loss": "Weight loss",
        "Abdominal mass": "Abdominal mass",
        "Unexplained rectal mass": "Unexplained rectal mass",
        "Anal ulceration/mass": "Anal ulceration/mass",
        "GP not concerned about cancer": "GP not concerned about cancer",
        "Patient declines or cannot complete the FIT test" : "Patient declines or cannot complete the FIT test",
        "FIT test not returned by the patient by day 21": "FIT test not returned by the patient by day 21",
        "FIT test not returned by the patient by day 7": "FIT test not returned by the patient by day 7",
        "FIT test spoiled or not completed by the patient": "FIT test spoiled or not completed by the patient",
        "FIT Negative": "FIT Negative",
        "FIT Positive": "FIT Positive",
        "Iron Deficiency Anaemia": "Iron deficiency anaemia",
        "Meets criteria for referral": "Meets criteria for referral",
        "Frailty": "Frailty",
        "Multiple comorbidities": "Multiple comorbidities",
    }

    # Initialize the list for mapped conditions
    mapped_conditions = []

    # Map general conditions
    for key, neo4j_condition in condition_mappings.items():
        if key in parsed_json:
            value = parsed_json[key]
            if value == "Yes":
                mapped_conditions.append(neo4j_condition)

    # Ensure "Patient is 50 years old or older" supersedes "Patient is 40 years old or older"
    if (
        "Patient is 50 years old or older" in mapped_conditions
        and "Patient is 40 years old or older" in mapped_conditions
    ):
        mapped_conditions.remove("Patient is 40 years old or older")  # Remove the less specific condition

    # Map FIT positive pathway results
    fit_positive = parsed_json.get("FIT positive pathway results", {})
    for key, value in fit_positive.items():
        if value == "Yes" and key in condition_mappings:
            mapped_conditions.append(condition_mappings[key])

    # Map FIT negative pathway results
    fit_negative = parsed_json.get("FIT negative pathway results", {})
    for key, value in fit_negative.items():
        if value == "Yes" and key in condition_mappings:
            mapped_conditions.append(condition_mappings[key])

    return mapped_conditions
