import streamlit as st
import pandas as pd
from io import StringIO
from datetime import datetime
from initialize_agent import create_langchain_agent
from guideline_recommendations import get_guideline_recommendations
from parse_and_summarize_pdf import parse_and_summarize_pdf
import json

# Add custom CSS for the subheader
st.markdown(
    """
    <style>
    .subheader {
        font-size: 16px;
        color: #666;
        margin-bottom: 20px;
    }
    .disabled {
        color: #999 !important;
        pointer-events: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize the agent for recommendations
# Neo4j connection details
uri= "neo4j+s://7739a51b.databases.neo4j.io"
username = "neo4j"
password = "Q9fhROhDv4_YRFy2U_4t5LCwYEeyspi7mu3YSHfTJuk" 

# Create the LangChain agent
agent = create_langchain_agent(uri, username, password)

# App title and subheader
st.title("Rapid CRC Pathway Tool")
st.markdown('<div class="subheader">Streamlined Urgent Cancer Referrals</div>', unsafe_allow_html=True)

# Dropdown selector for cancer type
selected_cancer = st.selectbox(
    "Select Cancer Type",
    options=["Colorectal Cancer", "Bowel Cancer (Disabled)", "Other Cancer (Disabled)"],
    index=0,
    help="Currently, only Colorectal Cancer is supported."
)

if "Disabled" in selected_cancer:
    st.warning("This option is currently not supported. Please select 'Colorectal Cancer (Enabled)'.")
    st.stop()

# Sidebar for file upload
st.sidebar.header("Upload PDFs")
uploaded_files = st.sidebar.file_uploader(
    "Upload one or more 2WW referral forms (PDFs)",
    type=["pdf"],
    accept_multiple_files=True,
)

# Persistent storage for results
if "results" not in st.session_state:
    st.session_state["results"] = []

if uploaded_files:
    st.sidebar.success(f"{len(uploaded_files)} file(s) uploaded successfully!")
    
    for uploaded_file in uploaded_files:
        # Check if this file has already been processed
        if any(result["Filename"] == uploaded_file.name for result in st.session_state["results"]):
            continue  # Skip reprocessing
        
        with st.spinner(f"Processing {uploaded_file.name}..."):
            try:
                # Parse and summarize the PDF
                summary, conditions = parse_and_summarize_pdf(uploaded_file)
                provided_conditions = json.dumps(conditions)
                patient_summary = f"Patient presents with the following provided conditions: {provided_conditions}"
                # Get recommendations and intermediate steps
                intermediate_steps, final_answer = get_guideline_recommendations(patient_summary, agent)

                # Store results in session state
                st.session_state["results"].append({
                    "Filename": uploaded_file.name,
                    "Patient Data": summary,
                    "Intermediate Steps": intermediate_steps,
                    "Final Answer": final_answer,
                })
                print(intermediate_steps, 'got here')

                # Display results for each file
                with st.expander(f"Results for {uploaded_file.name}"):
                    st.subheader("Recommendations")
                    st.text_area(f"Recommendations for {uploaded_file.name}", final_answer, height=150)

                    st.subheader("Extracted Patient Data")
                    st.text_area(f"Summary of {uploaded_file.name}", summary, height=300)
                   
                    # st.subheader("Intermediate Steps")
                    # st.text_area(f"Agent's Thought Process for {uploaded_file.name}", intermediate_steps, height=300)

            except Exception as e:
                st.error(f"An error occurred while processing {uploaded_file.name}: {e}")

    # Provide a consolidated download button for all results
    if st.session_state["results"]:
        # Convert results to a pandas DataFrame
        df = pd.DataFrame(st.session_state["results"])

        # Convert DataFrame to CSV
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()

        # Generate a dynamic filename with the current timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"all_results_{timestamp}.csv"
        # Add a download button for the CSV
        st.download_button(
            label="Download All Results as CSV",
            data=csv_data,
            file_name=filename,
            mime="text/csv",
        )
