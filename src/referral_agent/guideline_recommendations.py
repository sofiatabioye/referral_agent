### Module 3: Recommendation Generation ###
import io
import sys
import re

def strip_ansi_codes(text):
    """Removes ANSI escape codes from a string."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def get_guideline_recommendations(summary, agent_executor):
    """Generates recommendations and captures intermediate steps."""
    
    # Prepare the prompt
    # prompt = f"""
    #     Based on the following patient data extracted from a patient's 2WW referral form:
    #     {summary}

    #     Please provide recommendations for the patient. Use the medical guidelines tool to inform your response.
    # """
    # Capture verbose output
    old_stdout = sys.stdout
    sys.stdout = mystdout = io.StringIO()
    verbose_logs = ""

    try:
        response = agent_executor.invoke({"input": summary})
        # Retrieve verbose logs
        verbose_logs = mystdout.getvalue()

        # Extract intermediate steps and final answer
        intermediate_steps = strip_ansi_codes(verbose_logs)
        final_answer = response.get("output", "No recommendation provided.")

        return intermediate_steps, final_answer
    except Exception as e:
        print(f"Error: {e}")
        # Return a fallback value in case of error
        return "Error occurred during processing.", "No recommendation provided."
    finally:
        sys.stdout = old_stdout

   
