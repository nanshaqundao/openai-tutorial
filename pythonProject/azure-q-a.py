import gradio as gr
import os
import requests
from pydub import AudioSegment
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure OpenAI API settings
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")


def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def get_token():
    return read_file('token.txt').strip()


def transcribe_audio(audio_path):
    url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT_NAME}/audio/transcriptions?api-version=2023-09-01-preview"
    headers = {
        "Authorization": f"Bearer {get_token()}",
    }
    with open(audio_path, "rb") as audio_file:
        files = {"file": ("audio.wav", audio_file, "audio/wav")}
        response = requests.post(url, headers=headers, files=files)
    if response.status_code == 200:
        return response.json()["text"]
    else:
        raise Exception(f"Transcription failed: {response.text}")


def chat_with_ai(messages):
    url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT_NAME}/chat/completions?api-version=2023-05-15"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_token()}"
    }
    payload = {
        "messages": messages,
        "max_tokens": 800,
        "temperature": 0.7,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "top_p": 0.95,
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Chat completion failed: {response.text}")


def process_audio(audio):
    if audio is None:
        return "No audio recorded", "Please record some audio first."

    # Save the audio file
    audio_path = "temp_audio.wav"
    AudioSegment.from_file(audio).export(audio_path, format="wav")

    # Transcribe the audio
    transcription = transcribe_audio(audio_path)

    # Read the code file and PowerPoint content
    code = read_file("path_to_your_code_file.py")  # Replace with the actual path
    ppt_content = read_file("path_to_your_ppt.md")  # Replace with the actual path

    # Prepare messages for the chat API
    messages = [
        {"role": "system", "content": f"""You are a helpful assistant for a Q&A session about a specific Python program and its associated presentation. 
        You have knowledge about our program and presentation, and can provide insights about both. 

        Here's the code of the program you should be familiar with:

        {code}

        And here's the content of the PowerPoint presentation (in Markdown format):

        {ppt_content}

        Please answer questions about this code, its functionality, the presentation content, and provide explanations or suggestions when asked. 
        You can refer to both the code and the presentation content in your answers."""},
        {"role": "user", "content": transcription}
    ]

    # Get response from chat API
    response = chat_with_ai(messages)

    # Clean up the temporary audio file
    os.remove(audio_path)

    return transcription, response


# Create Gradio interface
iface = gr.Interface(
    fn=process_audio,
    inputs=gr.Audio(type="filepath", label="Record Audio"),
    outputs=[
        gr.Textbox(label="Transcription"),
        gr.Textbox(label="AI Response")
    ],
    title="Voice Q&A System (Azure OpenAI API)",
    description="Click the microphone to start recording, click again to stop. The system will transcribe your audio and provide an AI-generated answer about the program and its presentation."
)

# Launch the interface
iface.launch()