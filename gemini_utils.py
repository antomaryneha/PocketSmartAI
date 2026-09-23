import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)


def ask_gemini(prompt, image_bytes=None, mime_type=None):
    try:
        if image_bytes:
            contents = [
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type or "image/jpeg"
                ),
                prompt
            ]
        else:
            contents = prompt

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=contents
        )

        return response.text

    except Exception as e:
        error_message = str(e)

        if "429" in error_message or "quota" in error_message.lower():
            return (
                "Gemini API quota has been reached. "
                "Please wait and try again later."
            )

        return "Sorry, Gemini could not generate a recommendation right now."