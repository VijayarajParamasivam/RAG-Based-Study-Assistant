## Education Assistant

## Project Overview

This Education Chatbot is an interactive AI-powered tool designed to assist students in understanding complex anatomy topics. By leveraging provided educational resources, the chatbot provides real-time answers, flow charts, tables, chapter-wise answers for given exercises (in PDF format) and interactive diagrams. It also supports image based searches. The project aims to create an accessible, engaging, and user-friendly platform that supports students in mastering anatomy concepts.


## Features

- **Real-Time Query Resolution:** Instant responses to user questions about anatomy.
- **Interactive Diagrams, Tables and Flowcharts:** Visual aids to enhance understanding of complex anatomical structures.
- **Image Based Queries:** Supports Image Based Queries.
- **Exercise Answers:** Provides answers for Book Exercises in PDF format.

## Architecture

- **Frontend:** 
  - User-friendly interface made with Streamlit.
- **Backend:** 
  - Powered by a Gemini AI API and OpenCV, provides well structured and informational responses along with relevant images, tables and flowcharts.
- **Data Sources:** 
  - The chatbot accesses a curated database of anatomy textbooks  provided  to ensure the accuracy of information provided.

## Technologies Used

- **Programming Languages:** Python
- **Tools:** Gemini API, OpenCV, Streamlt, Chroma DB, PyPDF, Pillow, GraphViz

## Installation

To set up the Anatomy Education Chatbot locally, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Saikabilane/RAG-final.git

2. **Navigate to the project directory:**

   ```bash
   cd RAG-final

3. **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    ```
    ```bash
    venv\Scripts\activate
    ```

4. **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Initial Setup

1. **Get your API key:**

    - Get your Gemini API key from https://aistudio.google.com/app/apikey
    - Use the API key in place of "Your-API-key" in my_script.py and st_app.py

2. **Prerequisites:**

    - Install Graphiz software on tour system for generating flowchart based responses.
   
4. **Create a folder:**

   ```bash
   mkdir images
   ```

5. **Run the python files**

   ```bash
   python imageExtract.py
   ```
   ```bash
   python img_fetch.py
   ```
   ```bash
   python my_script.py
   ```

## Usage

1. **Run the Application:**

   ```bash
   streamlit run .\st_app.py
   ```
2. **Ask your Queries to the Education Assistant chatbot**

   

