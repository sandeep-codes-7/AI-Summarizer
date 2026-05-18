import streamlit as st
from urllib.parse import urlparse, parse_qs
import re
import yt_dlp
import whisper
from ollama import chat
from ollama import ChatResponse
import tempfile
import os

# Page config
st.set_page_config(page_title="AI summerizer", page_icon="🎬", layout="centered")

# Title
st.title("AI summarizer")

# YouTube URL input
youtube_url = st.text_input(
    "Enter YouTube URL",
    placeholder="https://www.youtube.com/watch?v=...",
)

# Output area placeholder
output_placeholder = st.empty()


# def extract_video_id(url: str) -> str | None:
#     """Extract YouTube video ID from various URL formats."""
#     patterns = [
#         r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
#         r"(?:youtu\.be\/)([0-9A-Za-z_-]{11})",
#         r"(?:embed\/)([0-9A-Za-z_-]{11})",
#     ]
#     for pattern in patterns:
#         match = re.search(pattern, url)
#         if match:
#             return match.group(1)
#     return None


def get_transcript(url: str) -> str:

    # ydl_opts = {"format": "bestaudio/best", "outtmpl": "audio.%(ext)s"}

    # with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    #     ydl.download([url])

    model = whisper.load_model("base")

    # result = model.transcribe("audio.webm")
    # print(result["text"])
    # return result
    with tempfile.TemporaryDirectory() as temp_dir:

        audio_path = os.path.join(temp_dir, "audio.%(ext)s")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': audio_path,
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

            downloaded_file = None

            for file in os.listdir(temp_dir):
                if file.startswith("audio"):
                    downloaded_file = os.path.join(temp_dir, file)
                    break

            result = model.transcribe(downloaded_file)

            return result
            

def summarize(transcript: str) -> str:
    response: ChatResponse = chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": "Please provide a clear, well-structured summary of the following "
                "YouTube video transcript. Include:\n"
                "- A brief overview (2-3 sentences)\n"
                "- Key points as bullet points\n"
                "- A short conclusion\n\n"
                f"Transcript:\n{transcript["text"]}",
            },
        ]
    )
    print(response.message.content)

    return response.message.content

st.sidebar.title("AI Summarizer")
# Summarize button
if st.button("Summarize", type="primary", use_container_width=True):
    if not youtube_url.strip():
        st.warning("Please enter a YouTube URL.")
    else:
        video_id = youtube_url.strip()
        if not video_id:
            st.error("Could not parse a valid YouTube video ID from that URL.")
        else:
            with st.spinner("Fetching transcript…"):
                try:
                    transcript = get_transcript(video_id)
                except RuntimeError as e:
                    st.error(str(e))
                    st.stop()

            st.success("Transcript fetched! Generating summary…")
            try:
                with st.spinner("Generating Summary for you..."):
                    try:
                        summary = summarize(transcript)
                        with output_placeholder.container():
                            md = st.empty()
                            md.markdown(summary)
                    except Exception as e:
                        st.error("Error generating summary. please try again...")
            except Exception as e:
                st.error(f"Error calling AI: {e}")
