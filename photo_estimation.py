import os
import json
import base64
from dotenv import load_dotenv
from mistralai.client import Mistral
from validator import validate_nutrition

load_dotenv()
client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

def encode_image(image_path):
    """
    Converts an image file to base64 string so it can be sent via API.
    Supports jpg, png, and most common image formats.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def estimate_from_photo(image_path):
    """
    Takes a path to a food photo and returns estimated nutrition.
    The AI identifies what food is in the image and estimates calories.
    """
    try:
        image_data = encode_image(image_path)

        response = client.chat.complete(
            model="pixtral-12b",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        },
                        {
                            "type": "text",
                            "text": (
                                "You are a nutrition estimation assistant. "
                                "Look at this food image and estimate the nutrition. "
                                "Respond ONLY with valid JSON, no extra text. "
                                "Use this exact format: "
                                '{"food": "string", "calories": number, "protein_g": number, '
                                '"carbs_g": number, "fat_g": number, '
                                '"portion_description": "string"}'
                            )
                        }
                    ]
                }
            ]
        )

        raw = response.choices[0].message.content.strip()

        # Remove markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        result = json.loads(raw)
        result["source"] = "photo"

        is_valid, cleaned, errors = validate_nutrition(result)

        if not is_valid:
            return {"error": f"Invalid nutrition data: {errors}"}

        cleaned["portion_description"] = result.get("portion_description", "")
        return cleaned

    except Exception as e:
        return {"error": str(e)}