import os
import json
from dotenv import load_dotenv
from mistralai.client import Mistral

load_dotenv()
client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

def estimate_from_text(food_description):
    """
    Takes a free-text food description in any language.
    Returns estimated nutrition as a dictionary.
    Examples: "2 oeufs brouillés", "a bowl of harira", "تفاحة متوسطة"
    """
    try:
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {"role": "system", "content": (
                    "You are a nutrition estimation assistant. "
                    "The user will describe a food or meal in any language. "
                    "Estimate the nutrition and respond ONLY with valid JSON, no extra text. "
                    "Use this exact format: "
                    '{"food": "string", "calories": number, "protein_g": number, "carbs_g": number, "fat_g": number, "portion_description": "string"} '
                    "The portion_description field should describe the portion in the same language the user used."
                )},
                {"role": "user", "content": food_description}
            ]
        )
        raw = response.choices[0].message.content.strip()
        result = json.loads(raw)
        result["source"] = "ai_text"
        return result
    except Exception as e:
        return {"error": str(e)}