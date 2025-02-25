### Module 3: Recommendation Generation ###

def get_guideline_recommendations(text_summary, agent_executor):
    """
    Generates recommendations based on a provided text summary of patient data.
    
    Args:
        text_summary (str): A pre-extracted summary of patient data.
        agent_executor: The initialized agent executor for processing the prompt.
    
    Returns:
        str: Recommendations generated by the agent.
    """
    print("Summary of Patient Data: ")
    print(text_summary)

    prompt = f"""
    Based on the following patient data extracted from a medical document:

    {text_summary}

    Please provide guideline-based recommendations for the patient's 2WW referral form. Use the medical guidelines stored in the system to inform your response.
    """

    response = agent_executor.invoke({"input": prompt, "chat_history": ""})
    return response

### Example Usage ###
    # - Name: John Doe
    # - Age: 45
    # - Gender: Male
    # - Symptoms: Unexplained rectal bleeding, abdominal mass
    # - FIT result: Negative (Value: 3)
    # - WHO Performance status: Grade 1
    # - Additional History: Weight loss (5 kg in the past 2 months)
if __name__ == "__main__":
    # Replace this text with the summary of patient data
    text_summary = """
    Can you tell me the fit result of previous patient
    """
    
    from initialize_agent import initialize_agent  # Import agent initialization logic
    
    # Initialize the agent executor
    agent_executor = initialize_agent()
    
    # Generate recommendations
    recommendations = get_guideline_recommendations(text_summary, agent_executor)

    print("Recommendations:")
    print(recommendations)
