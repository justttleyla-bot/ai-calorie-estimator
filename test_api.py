import os
from dotenv import load_dotenv
from mistralai.client import Mistral

class FoodEntry:
    def __init__(self, name, calories):
        self.name = name
        self.calories = calories

    def describe(self):
        return f"{self.name}: {self.calories} kcal"

load_dotenv()
client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

def ask_ai(question):
    try:
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {"role": "user", "content": question}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Something went wrong: {e}"


import json

def estimate_calories(food_description):
    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[
            {"role": "system", "content": (
                "You are a nutrition estimation assistant. "
                "Always respond ONLY with valid JSON, no extra text, no explanations. "
                "Use this exact format: "
                '{"food": "string", "calories": number, "protein_g": number, "carbs_g": number, "fat_g": number}. '
                "Examples: "
                'Input: "a banana" -> {"food": "banana", "calories": 105, "protein_g": 1.3, "carbs_g": 27, "fat_g": 0.4}. '
                'Input: "tasse de lentilles cuites" -> {"food": "cooked lentils, 1 cup", "calories": 230, "protein_g": 18, "carbs_g": 40, "fat_g": 0.8}.'
            )},
            {"role": "user", "content": f"Estimate nutrition for: {food_description}"}
        ]
    )
    raw_text = response.choices[0].message.content
    return json.loads(raw_text)


def log_to_file(question, answer):
    with open("log.txt", "a", encoding="utf-8") as file:
        file.write(f"Q: {question}\n")
        file.write(f"A: {answer}\n")
        file.write("---\n")

q1 = "Say hello and tell me one fun fact about Morocco."
a1 = ask_ai(q1)
log_to_file(q1, a1)
print(a1)

entry1 = FoodEntry("Banana", 105)
entry2 = FoodEntry("Grilled Chicken Breast", 165)

print(entry1.describe())
print(entry2.describe())


result = estimate_calories("كاسة شاي بالحليب")
print(f"Food: {result['food']}")
print(f"Calories: {result['calories']} kcal")
print(f"Protein: {result['protein_g']}g")
print(f"Carbs: {result['carbs_g']}g")
print(f"Fat: {result['fat_g']}g")