import os
import json
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
import fitz  # PyMuPDF
from pdf2image import convert_from_bytes
import pytesseract
from io import BytesIO


def extract_text_with_ocr(file_path):
    """
    Extracts text from a PDF file using both PyMuPDF for selectable text and OCR for scanned pages.
    Accepts a file path.
    """
    text = ""
    try:
        # Open the file using PyMuPDF
        with open(file_path, "rb") as file:
            pdf_document = fitz.open(stream=file.read(), filetype="pdf")
        
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                page_text = page.get_text()

                if page_text.strip():
                    text += page_text
                else:
                    # Use OCR if no selectable text
                    file.seek(0)  # Reset file pointer for pdf2image
                    images = convert_from_bytes(file.read(), first_page=page_num + 1, last_page=page_num + 1)
                    for image in images:
                        text += pytesseract.image_to_string(image)
    except Exception as e:
        raise ValueError(f"Error processing the PDF file: {e}")
    return text


def parse_and_summarize_pdf(file_path, output_path):
    """
    Parses and summarizes a PDF file with mixed content (selectable text and scanned images).
    Reads from `file_path` and saves the result to `output_path` as a JSON file.
    """
    # Step 1: Extract text
    raw_text = extract_text_with_ocr(file_path)
    
    # Step 2: Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=8000, chunk_overlap=100)
    split_docs = text_splitter.split_text(raw_text)

    # Step 3: Use LLM for summarization
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,
    )
    summaries = []

    
    for chunk in split_docs:
        prompt = f"""
            This text is from a 2WW referral form for colorectal cancer. Extract the following details and format the output as JSON. Use the rules below to ensure accuracy:

            0. ** FIT Result
            - If the FIT result is less than 10 ugHb/g, this will be recorded as Negative, while greater than or equal to 10 ugHb/g will be Positive. This can be found in the text as 'FIT result: ...'.

            1. **FIT Positive Pathway Results Rules**:
            - For each parameter in the FIT positive pathway results (Rectal bleeding, Change in bowel habit, Weight loss, Iron Deficiency Anaemia), check if it is mentioned in the text.
            - If the parameter is present and has a FIT value (e.g., 'FIT result: ...'), mark it as 'Yes' and include the FIT value.
            - If the parameter is present and has recorded values (e.g. Amount, MCV) but no FIT value, mark it as 'Yes' but indicate 'FIT value: Not provided'.
            - If the parameter has no values at all, mark it as 'No'.

            2. **FIT Negative Pathway Results Rules**:
            - For FIT-negative patients with Iron Deficiency Anaemia (IDA), extract the following:
                - Indicate if the patient meets all criteria for referral:
                - Aged 40 years or over: Yes/No (Check the recorded age and compare it to 40 years)
                - FIT Negative: Yes/No (This is a "Yes" if FIT result is less than 10), FIT result: [Value/Not provided]
                - Ferritin ≤45 µg/L: Yes/No (This is a "Yes" if Ferritin value ≤45µg/L), Ferritin: [Value/Not provided]
                - Iron deficiency anaemia: Yes/No (Yes if Hb value less than 130 g/L (13 g/dL) in men or 115 g/L (11.5 g/dL) in non-menstruating women). Ensure that Hb values reported in g/L are compared to thresholds directly in g/L, Hb: [Value/Not provided].

            3. **General Formatting Rules**:
            - Provide the output as a JSON object with the following structure:
            {{
                "Name": [Value],
                "Age": [Value],
                "Gender": [Value],
                "Date of birth": [Value],
                "Address": [Value],
                "Hospital number": [Value],
                "Landline number:": [Value],
                "Mobile number:": [Value],
                "Patient consents to be contacted by text on the above mobile?": [Yes/No],
                "Interpreter required": [Yes/No],
                "Patient has capacity to consent?": [Yes/No],
                "First Language": [Value],
                "GP declaration": [Value],
                "Registered GP details": [Value],
                "Date of Decision to refer": [Value],
                "Date of Referral:": [Value],
                "Name of referring GP:": [Value],
                "Any adult (16 years or over)":{{
                    "Abdominal mass": [Yes/No],
                    "Unexplained rectal mass": [Yes/No],
                    "Anal ulceration/mass": [Yes/No],
                }},
                "FIT result": {{
                    "value": [Value],
                    "status": ["Positive" / "Negative"]
                }},
                "FIT positive pathway results": {{
                    "Rectal bleeding": {{
                        "present": [Yes/No],
                        "FIT result": [Value/Not provided]
                    }},
                    "Change in bowel habit": {{
                        "present": [Yes/No],
                        "FIT result": [Value/Not provided]
                    }},
                    "Unexplained weight loss": {{
                        "present": [Yes/No],
                        "FIT result": [Value/Not provided],
                        "amount": [Value],
                        "duration": [Value],
                        "O/E Weight": [Value],
                        "O/E previous weight": [Value]
                    }},
                    "Iron Deficiency Anaemia": {{
                        "present": [Yes/No],
                        "FIT result": [Value/Not provided],
                        "Hb": [Value],
                        "MCV": [Value],
                        "Ferritin": [Value],
                    }}
                }},
                "FIT negative pathway results": {{
                    "Meets criteria for referral": [Yes/No],
                    "Aged 40 years or over": [Yes/No],
                    "FIT Negative": {{
                        "status": [Yes/No],
                        "FIT result": [Value/Not provided]
                    }},
                    "Ferritin ≤45 µg/L": {{
                        "status": [Yes/No],
                        "Ferritin": [Value/Not provided]
                    }},
                    "Anaemia": {{
                        "status": [Yes/No],
                        "Hb": [Value/Not provided]
                    }}
                    "Dipstick the urine": [Yes/No],
                    "Screen for Coeliac disease": [Yes/No],
                    "Renal function (urea, creatinine, eGFR)": [Yes/No],
                    "You have commenced iron treatment": [Yes/No],
                    "Date of iron treatment commencement": [Value],
                }},
                "FIT Negative Test Results": {{
                    "Ferritin": [Value],
                    "MCV": [Value],
                    "Hb": [Value],
                    "TTG": [Value],
                    "Urea": [Value],
                    "Creatinine": [Value],
                    "eGFR": [Value],
                }},
                "WHO Performance status": [Value],
                "Additional History": {{
                   "Last Consultation": [Value],
                   "Medical Hx": [Value],
                   "Allergies": [Value],
                   "Smoking status": [Value],
                   "Alcohol intake": [Value],
                   "Recent investigations": [Value], 
                   "Including FBC, Ferritin, U&Es (within 3 months), AND Urine dipstick, TTG if FIT negative": [Value],
                }}
            }}

            Text:
            {chunk}
        """
        response = llm.invoke(prompt)
        result = response.content if hasattr(response, "content") else str(response)
        summaries.append(result)

    # Combine all the chunks into a single JSON structure
    formatted_summary = "[" + ", ".join(summaries) + "]"

    # Step 1: Clean the formatted_summary string
    # Remove Markdown-like formatting (e.g., ```json) and unnecessary characters
    cleaned_summary = formatted_summary.replace("```json", "").replace("```", "").strip("[ ]")
    print(cleaned_summary)
    # Step 2: Parse the cleaned string into JSON
    try:
        parsed_json = json.loads(f"[{cleaned_summary}]")  # Treat the cleaned content as an array
        print("Valid JSON parsed successfully!")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        parsed_json = []

    # Combine all the chunks into a single JSON structure
    # formatted_summary = "\n".join(summaries)
    # Step 3: Save the parsed JSON to a file
    # output_file_path = "cleaned_combined_output.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(parsed_json, f, indent=4)

    print(f"Cleaned JSON saved to {output_path}")
    
    # # Save the summary to the output JSON file
    # with open(output_path, "w", encoding="utf-8") as output_file:
    #     json.dump(formatted_summary, output_file, indent=4)

    # print(f"Summary saved to {output_path}")


# Example Usage
def process_pdf_folder(input_folder, output_folder):
    """
    Processes all PDF files in the input folder and saves summaries to the output folder as JSON.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file_name in os.listdir(input_folder):
        if file_name.endswith(".pdf"):
            input_path = os.path.join(input_folder, file_name)
            output_path = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}_summary.json")
            print(f"Processing {file_name}...")
            parse_and_summarize_pdf(input_path, output_path)


# Example: Process all PDFs in the 'data' folder and save summaries to the 'results' folder
process_pdf_folder("data", "SampleIOV2WWFormsResultsv1")
