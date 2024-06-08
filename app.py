import os
import tempfile
import streamlit as st
import assemblyai as aai
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

def main():
    # Access the AssemblyAI API key from Streamlit secrets
    assemblyai_api_key = st.secrets["assemblyai_api_key"]
    aai.settings.api_key = assemblyai_api_key

    # Access the OpenAI API key from Streamlit secrets
    openai_api_key = st.secrets["openai_key"]
    chat = ChatOpenAI(openai_api_key=openai_api_key)

    # Streamlit interface
    st.title("Audio Transcription and Summary Generator")

    # Upload audio file
    uploaded_file = st.file_uploader("Choose an audio file", type=["m4a", "mp3"])

    if uploaded_file is not None:
        st.write("File successfully uploaded. Transcribing...")
        transcript = transcribe_audio(uploaded_file)
        context = transcript.text
        
        st.subheader("Transcript")
        st.write(context)

        # User input for question
        user_question = st.text_input("Enter your question:")

        if user_question:
            st.write("Generating answer...")
            assistant_answer = generate_answer(chat, context, user_question)
            st.subheader("Assistant's Answer")
            st.markdown(assistant_answer)

def transcribe_audio(uploaded_file):
    transcriber = aai.Transcriber()
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name

    transcript = transcriber.transcribe(temp_file_path)
    os.unlink(temp_file_path)
    return transcript

def generate_answer(chat, context, question):
    system_template = "You are a friendly research assistant. Your task is to use the provided context (an AI transcription of a user-uploaded audio file) to answer the user's questions accurately in an organized, concise, readable format. Always use markdown syntax like **bold** to improve readability."
    human_template = "{question}"

    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

    try:
        response = chat(chat_prompt.format_prompt(question=question, context=context).to_messages())
        return response.content
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    main()
