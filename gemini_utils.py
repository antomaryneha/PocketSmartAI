
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

        print("GEMINI REQUEST STARTED")

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                thinking_config=types.ThinkingConfig(
                    thinking_level="low"
                )
            )
        )

        print("GEMINI REQUEST SUCCESS")

        return response.text

    except Exception as e:

        error_message = str(e)

        print("GEMINI ERROR:", e)

        if "429" in error_message or "quota" in error_message.lower():

            return (
                "GEMINI_ERROR: API quota has been reached."
            )

        if "503" in error_message:

            return (
                "GEMINI_ERROR: Gemini service is temporarily busy."
            )

        if "404" in error_message:

            return (
                "GEMINI_ERROR: Gemini model was not found."
            )

        return f"GEMINI_ERROR: {e}"

