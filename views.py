import yt_dlp
import whisper
from ollama import chat
from ollama import ChatResponse

"""
basic workflow, this works in the terminal...
visit main.py for streamlit interface

https://github.com/sandeep-codes-7

"""
URL = input("enter url: ")

ydl_opts = {
    "format":"bestaudio/best",
    "outtmpl":"audio.%(ext)s"
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([URL])

model = whisper.load_model("base")

result = model.transcribe("audio.webm")

print(f"transcription: {result["text"]}")


response: ChatResponse = chat(model='qwen3:8b', messages=[
  {
    'role': 'user',
    'content': f'"{result["text"]}", it is a transcription of a lecture video, so please summarize for me in detail and dont miss any detail',
  },
])
print(response.message.content)