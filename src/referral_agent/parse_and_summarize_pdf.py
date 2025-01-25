### Module 2: PDF Processing and Summarization ###
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
import fitz  # PyMuPDF
from pdf2image import convert_from_bytes
import pytesseract
from io import BytesIO
from clean_json import clean_and_parse_json
from mapper import map_json_to_conditions

def extract_text_with_ocr(file):
    """
    Extracts text from a PDF using both PyMuPDF for selectable text and OCR for scanned pages.
    Accepts a file-like object (BytesIO).
    """
    text = ""
    try:
        # Open the file using PyMuPDF
        pdf_document = fitz.open(stream=file.read(), filetype="pdf")
        
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            page_text = page.get_text()

            if page_text.strip():
                text += page_text
            else:
                # Use OCR if no selectable text
                pdf_document.seek(0)  # Reset file pointer for pdf2image
                images = convert_from_bytes(file.read(), first_page=page_num + 1, last_page=page_num + 1)
                for image in images:
                    text += pytesseract.image_to_string(image)
    except Exception as e:
        raise ValueError(f"Error processing the PDF file: {e}")
    return text

def parse_and_summarize_pdf(file):
    """
    Parses and summarizes a PDF file with mixed content (selectable text and scanned images).
    Accepts a file-like object (BytesIO).
    """
    # Step 1: Extract text
    raw_text = extract_text_with_ocr(file)
    
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
            Extract relevant clinical details for colorectal cancer referrals from the following text:
            This text is from a 2WW referral form for colorectal cancer. Extract the following details and format the output as a structured summary in JSON. Use the rules below to ensure accuracy:
            
            0. ** FIT Result
            - If the FIT result is less than 10 ugHb/g, this will be recorded as Negative, while greater than or equal to 10 ugHb/g will be Positive.
            
            ** ANY ADULT (16 YEARS OR OVER)
            For each of the parameters below indicated under this section, extract the followinf 
                - Abdominal mass [Yes/No]
                - Unexplained rectal mass [Yes/No]
                - Anal ulceration/mass [Yes/No]
            1. **FIT Positive Pathway Results Rules**:
            - For each parameter in the FIT positive pathway results (Rectal bleeding, Change in bowel habit, Weight loss, Iron Deficiency Anaemia), check if it is mentioned in the text.
            - If the parameter is present and has a FIT value (e.g., 'FIT result: ...'), mark it as 'Yes' and include the FIT value.
            - If the parameter is present without a FIT value, mark it as 'Yes' but indicate 'FIT value: Not provided'.
            - If the parameter is not mentioned in the text, mark it as 'No'.

            2. **FIT Negative Pathway Results Rules**:
            - For FIT-negative patients with Iron Deficiency Anaemia (IDA), extract the following:
                - Indicate if the patient meets all criteria for referral:
                - Aged 40 years or over: Yes/No
                - FIT Negative: Yes/No (This is a "Yes" if FIT result is less than 10), FIT result: [Value/Not provided]
                - Ferritin ≤45 µg/L: Yes/No (This is a "Yes" if Ferritin value ≤45µg/L), Ferritin: [Value/Not provided]
                - Iron deficiency anaemia: Yes/No (Yes if Hb value less than 130 g/L (13 g/dL) in men or 115 g/L (11.5 g/dL) in non-menstruating women). Ensure that Hb values reported in g/L are compared to thresholds directly in g/L, Hb: [Value/Not provided].
                
            3. **General Formatting Rules**:
            - Provide a structured summary with the fields below.
            - Use the following format for the output:
                - Name: [Value]
                - Age: [Value]
                - Patient is 40 years old or older: [Yes/No]
                - Patient is 50 years old or older: [Yes/No]
                - Patient is less than 50 years old: [Yes/No]
                - Patient
                - Gender: [Value]
                - Address: [Value]
                - Hospital number: [Value]
                - GP declaration: [Value]
                - GP/Doctor details: [Value]
                - Referral date: [Yes/No]
                - Abdominal mass: [Yes/No]
                - Unexplained rectal mass: [Yes/No]
                - Anal ulceration/mass: [Yes/No]
                - FIT result: FIT [Positive/Negative]
                - FIT result value: [Value], 
                - FIT positive pathway results:
                    - Rectal bleeding: [Yes/No]
                    - Change in bowel habit: [Yes/No]
                    - Weight loss: [Yes/No]
                    - Iron Deficiency Anaemia: [Yes/No]
                - FIT negative pathway results:
                    - Meets criteria for referral: [Yes/No]
                    - Aged 40 years or over: [Yes/No]
                    - FIT Negative: [Yes/No]
                    - Ferritin ≤45 µg/L: [Yes/No]
                    - Ferritin: [Value/Not provided]
                    - Anaemia: [Yes/No],
                    - Hb: [Value/Not provided]
                - WHO Performance status: [Value]
                - Additional History: [Value e.g. Weight loss, Abdominal mass, Frailty, Multiple comorbidities, Vague symptom etc.]
                - GP not concerned about cancer: [Yes/No]
                - Patient declines or cannot complete the FIT test: [Yes/No]
                - FIT test not returned by the patient by day 21: [Yes/No]
                - FIT test not returned by the patient by day 7: [Yes/No]
                - FIT test spoiled or not completed by the patient: [Yes/No]
                - FIT Negative: [Yes/No]
                - FIT Positive: [Yes/No]
                - Iron Deficiency Anaemia: [Yes/No]
                - Frailty: [Yes/No]
                - Multiple comorbidities: [Yes/No]
                - Vague symptom: [Yes/No]

            
            Text:
            {chunk}
            """
        response = llm.invoke(prompt)
        result = response.content if hasattr(response, "content") else str(response)
        summaries.append(result)

    # Format the final structured summary
    formatted_summary = "\n".join(summaries)
    try:
        cleaned_data = clean_and_parse_json(formatted_summary)
        conditions = map_json_to_conditions(cleaned_data)
        return cleaned_data, conditions
    except Exception as e:
        print(f"Error: {e}")
