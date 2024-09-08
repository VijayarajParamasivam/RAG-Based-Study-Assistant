import streamlit as st
import chromadb
import google.generativeai as genai
import pandas as pd
from fpdf import FPDF
import graphviz
import cv2
import os

# Load image and table data
pictures = pd.read_csv("./image_filenames.csv")
tables = pd.read_csv("./csv_filenames.csv")
pics_loc = pictures['Image Name']
tabs_loc = tables['Image Name']
pics_loc = list(pics_loc)
tabs_loc = list(tabs_loc)
texts = pictures['Description']
tabls = tables['Description']
texts = list(texts)
tabls = list(tabls)

# Google GenAI and Chroma configurations
api_key = "AIzaSyBt41MC3ZSxYlBktQH0WN_OFP45Jz7zjYs"
for_vision = "AIzaSyDWw26GAw7rq2CS4TJxuqGE2mrs6K8kmbM"
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

chroma_client = chromadb.PersistentClient(path="./collection")
collections = chroma_client.get_collection(name="my_collection")
img_collections = chroma_client.get_collection(name="images")
tables = chroma_client.get_collection(name="tables")
bookBack = chroma_client.get_collection(name="book_back")

# Streamlit interface
st.title("Education Assistant")
prompt = st.text_input("Enter your query here: ")

# Functions for different operations
def ask_query(prompt):
    results = collections.query(query_texts=[prompt], n_results=2)
    return results['documents']

def get_bookBack(prompt):
    results = bookBack.query(query_texts=[prompt], n_results=15)
    return results['documents']

def ask_img(prompt):
    results = img_collections.query(query_texts=[prompt], n_results=1)
    if results["distances"][0][0] >= 1:
        results = []
        return results
    return results['documents']

def ask_tab(prompt):
    results = tables.query(query_texts=[prompt], n_results=1)
    if results["distances"][0][0] >= 1.5:
        results = []
        return results
    return results['documents']

def generate_flowchart(text_description):
    dot = graphviz.Digraph()
    dot.attr(rankdir='LR', size='10,10')

    lines = text_description.strip().split('\n')
    for line in lines:
        if '->' in line:
            parts = line.split('->')
            start = parts[0].strip()
            end = parts[1].strip()
            dot.node(start, shape='box', style='filled', fillcolor='lightyellow')
            dot.node(end, shape='box', style='filled', fillcolor='lightyellow')
            dot.edge(start, end)
        else:
            dot.node(line.strip(), shape='box', style='filled', fillcolor='lightyellow')

    output_file = 'flowchart'
    dot.render(filename=output_file, format='png', cleanup=True)

def book_back(prompt):
    data = get_bookBack(prompt=prompt)
    response = model.generate_content(f"Retrieve all the questions from the chapter specified in '{prompt}', starting with question 1 and ending with the very last question of the chapter. Do not skip any questions in between. After providing each question, give the corresponding answer immediately from {data}. Ensure that all questions are included, and the answers follow directly after each respective question in a sequential and comprehensive manner.")
        
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    content_lines = response.text.splitlines()
    
    for line in content_lines:
        if line.strip() != "":
            pdf.multi_cell(190, 10, line.encode('latin1', 'replace').decode('latin1'))
        else:
            pdf.ln()
    pdf_output = "book_back_questions.pdf"
    pdf.output(pdf_output)
    with open(pdf_output, "rb") as pdf_file:
        st.download_button(label="Download PDF", data=pdf_file, file_name=pdf_output, mime="application/pdf")
    
    return response.text

# Image comparison function
def compare_image(uploaded_image_path):
    existing_image_folder = "./images"
    uploaded_image = cv2.imread(uploaded_image_path)

    if uploaded_image is None:
        st.error("Uploaded image could not be loaded.")
        return

    for image_name in os.listdir(existing_image_folder):
        existing_image_path = os.path.join(existing_image_folder, image_name)
        existing_image = cv2.imread(existing_image_path)

        if existing_image is None:
            continue

        if uploaded_image.shape == existing_image.shape:
            difference = cv2.subtract(uploaded_image, existing_image)
            b, g, r = cv2.split(difference)

            if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
                st.success(f"Uploaded image matches with {image_name}")
                index = int(pics_loc.index(image_name))
                imgSummary = model.generate_content(f"Explain like, this image describes...and elaborate the data in {texts[index]}")
                st.image(existing_image_path)
                st.write(imgSummary.text)
                return

    st.warning("No matching image found in the folder.")

def ask(prompt):
    temp_dir = "./temp"
    
    # Ensure temp directory exists
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    # Handle image upload for comparison
    uploaded_file = st.file_uploader("Upload an image to compare with existing images", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Create a temporary image path
        temp_image_path = os.path.join(temp_dir, uploaded_file.name)
        
        # Save the uploaded image file
        with open(temp_image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Call the comparison function
        compare_image(temp_image_path)
    else:
        st.warning("Please upload an image for comparison.")
    
    # Handle the main prompt processing
    if prompt:
        x = ask_img(prompt=prompt)
        y = ask_tab(prompt=prompt)
        data = ask_query(prompt)
        
        # Check if book back questions are requested
        questions = model.generate_content(f"If the user query, '{prompt}', explicitly asks for book back answers for a specific chapter, respond with only 'Yes'. Otherwise, respond with 'No'.")
        if 'Yes' in questions.text:
            given = book_back(prompt=prompt)
        
        # Check for flowchart request
        flowchart_response = model.generate_content(
            f"Please check the following user prompt and determine if it is requesting the generation of a flowchart. "
            f"Respond with 'True' if the prompt specifically asks for a flowchart. "
            f"Only respond with 'True' if the request is explicit. "
            f"Otherwise, respond with 'False'. For example, if the prompt is 'Generate a flowchart of the process', return 'True'. "
            f"If the prompt is 'Describe the process in detail', return 'False'.\n\nUser Prompt: {prompt}"
        )
        if 'True' in flowchart_response.text:
            flowchart_description = model.generate_content(
                f"Transform the following {data} into a flowchart format. Ensure each step is correctly connected with arrows ('->') indicating the flow from one step to the next.\n"
                f"Use the format: 'Step1 -> Step2\nStep2 -> Step3\n... -> End'.\n"
                f"Each step should be connected to the next with '->' in the order they appear.\n\nData: {data}"
            )
            generate_flowchart(flowchart_description.text)
            st.image("./flowchart.png")

        title_res = model.generate_content(f"Provide an appropriate title for the answer {prompt} of content. only that title.")
        response = model.generate_content(f"Using this data: {data}, answer to this prompt: {prompt}. if you don't find any data, just don't answer the question. If the {prompt} specifies for a table, then tabulate the obtained data and display it.")

        st.header(title_res.text)
        st.write(response.text)

        if x:
            val = texts.index(x[0][0])
            img = "./images/" + str(pics_loc[int(val)])
            st.image(img)

        if y:
            value = tabls.index(y[0][0])
            tab = "./tables/" + str(tabs_loc[int(value)])
            st.image(tab)
    else:
        st.header("Hi. I am here to assist you.")
        st.write("Tell me how I can help you.")


ask(prompt=prompt)