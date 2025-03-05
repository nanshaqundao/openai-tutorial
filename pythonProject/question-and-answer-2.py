import gradio as gr
import os
from openai import OpenAI
from pydub import AudioSegment
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if api_key is None:
    raise ValueError("OpenAI API key is missing. Please set it in the environment variables.")

client = OpenAI(api_key=api_key)


def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def transcribe_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcription.text


def chat_with_ai(messages):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # or "gpt-4" if you have access
        messages=messages,
        max_tokens=800,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message.content


def process_audio(audio):
    if audio is None:
        return "No audio recorded", "Please record some audio first."

    # Save the audio file
    audio_path = "temp_audio.wav"
    AudioSegment.from_file(audio).export(audio_path, format="wav")

    # Transcribe the audio
    transcription = transcribe_audio(audio_path)

    # Read the code file and PowerPoint content
    code = read_file("question-and-answer-2.py")  # Replace with the actual path
    ppt_content = read_file("ppt.md")  # Replace with the actual path

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
    title="Voice Q&A System (OpenAI API)",
    description="Click the microphone to start recording, click again to stop. The system will transcribe your audio "
                "and provide an AI-generated answer about the program and its presentation."
)

# Launch the interface
iface.launch()