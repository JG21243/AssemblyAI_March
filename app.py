import tempfile
import os
import streamlit as st
import assemblyai as aai
from langchain.llms import OpenAI

# Access the AssemblyAI API key from Streamlit secrets
assemblyai_api_key = st.secrets["assemblyai_api_key"]

# Create AssemblyAI settings object with the API key
aai.settings.api_key = assemblyai_api_key

# Access the OpenAI API key from Streamlit secrets
openai_api_key = st.secrets["openai_key"]
openai_client = OpenAI(openai_api_key=openai_api_key)

# Streamlit interface
st.title("Audio Transcription and Summary Generator")

# Upload audio file
uploaded_file = st.file_uploader("Choose an audio file", type=["m4a", "mp3"])

if uploaded_file is not None:
    st.write("File successfully uploaded. Transcribing...")
    
    # Create a temporary file and write the uploaded file's bytes to it
    transcriber = aai.Transcriber()
    with tempfile.NamedTemporaryFile(delete=False) as tfile:
        tfile.write(uploaded_file.read())
        tfile_path = tfile.name
    
    # Transcribe audio file
    transcript = transcriber.transcribe(filename=tfile_path)
    
    # Poll for result or use webhooks in a real application
    context = transcript.text
    st.subheader("Transcript")
    st.write(transcript.text)

    # Clean up the temporary file
    os.unlink(tfile_path)

    # User input for question
    user_question = st.text_input("Enter your question:")
    
    if user_question:
        st.write("Generating answer...")
        
        # Generate answer
        def generate_answer(context_data, user_question):
            try:
                response = openai_client([
                    {
                        "role": "system",
                        "content": "You are a friendly research assistant. Your task is to use the provided context (an AI transcription of a user-uploaded audio file) to answer the user's questions accurately in an organized, concise, readable format. Always use markdown syntax like **bold** to improve readability."
                    },
                    {
                        "role": "assistant",
                        "content": f"Here is the context: {context_data}"
                    },
                    {
                        "role": "user",
                        "content": user_question
                    }
                ])
                return response.content.strip()
            except Exception as e:
                return str(e)
        
        # Display assistant's answer
        assistant_answer = generate_answer(context, user_question)
        st.subheader("Assistant's Answer")
        st.write(assistant_answer)
