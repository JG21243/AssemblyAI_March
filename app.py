import tempfile
import os
import streamlit as st
from assemblyai import Client as AAI_Client
from openai import OpenAI

# Initialize API clients with secrets
openai_client = OpenAI(api_key=st.secrets["general"]["openai_key"])
assemblyai_api_key = st.secrets["api_keys"]["assemblyai"]
assemblyai_client = AAI_Client()

# Streamlit interface
st.title("Audio Transcription and Summary Generator")

# Upload audio file
uploaded_file = st.file_uploader("Choose an audio file", type=["m4a", "mp3"])

if uploaded_file is not None:
    st.write("File successfully uploaded. Transcribing...")
    
    # Create a temporary file and write the uploaded file's bytes to it
    with tempfile.NamedTemporaryFile(delete=False) as tfile:
        tfile.write(uploaded_file.read())
        tfile_path = tfile.name
    
    # Transcribe audio file
    transcript_result = assemblyai_client.transcribe(filename=tfile_path)
    
    # Poll for result or use webhooks in a real application
    transcript = transcript_result.get('text')
    st.subheader("Transcript")
    st.write(transcript)

    # Clean up the temporary file
    os.unlink(tfile_path)

    # User input for question
    user_question = st.text_input("Enter your question:")
    
    if user_question:
        st.write("Generating answer...")
        
        # Generate answer
        def generate_answer(context_data, user_question):
            try:
                response = client.chat.completions.create(model="gpt-4",
                messages=[
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
                ],
                max_tokens=5000,
                n=1,
                stop=None,
                temperature=0.0)
                return response['choices'][0]['message']['content'].strip()
            except Exception as e:
                return str(e)
        
        # Display assistant's answer
        assistant_answer = generate_answer(context, user_question)
        st.subheader("Assistant's Answer")
        st.write(assistant_answer)
