import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)


def ask_gemini(prompt, image_bytes=None, mime_type=None):

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


    for attempt in range(3):

        try:

            print(
                f"GEMINI REQUEST STARTED "
                f"(attempt {attempt + 1}/3)"
            )

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


            # Temporary Gemini server problem
            if "503" in error_message:

                if attempt < 2:

                    print(
                        "Gemini is temporarily busy. "
                        "Retrying..."
                    )

                    time.sleep(3)

                    continue

                return (
                    "GEMINI_ERROR: "
                    "Gemini service is temporarily busy."
                )


            # API quota
            if (
                "429" in error_message
                or "quota" in error_message.lower()
            ):

                return (
                    "GEMINI_ERROR: "
                    "API quota has been reached."
                )


            # Model not found
            if "404" in error_message:

                return (
                    "GEMINI_ERROR: "
                    "Gemini model was not found."
                )


            return f"GEMINI_ERROR: {e}"


    return "GEMINI_ERROR: Gemini request failed."