import openai
import os
import json
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

with open('path_to/structured_products.json', 'r') as json_file:
    products = json.load(json_file)

def suggest_clothes(client_query, products):
    product_list_str = ""
    for product in products:
        product_list_str += f"- Name: {product['name']}, Description: {product['description']}, " \
                            f"Category: {product['category']}, Style: {product['style']}, " \
                            f"Season: {product['season']}\n"

    prompt = f"""
    You are an AI assistant for an online clothing store. Below is a list of products, each with its name, description, category, style, season, and image folder.

    Product List:
    {product_list_str}

    A customer has submitted the following inquiry: "{client_query}"

    Your task:
    1. Review the provided inquiry carefully.
    2. Select the most appropriate clothing items from the product list based on the client's needs.
    3. For each selected item, provide:
       - Name
       - Description
       - Category
       - Style
       - Season
       - Image folder

    Ensure that your recommendations are relevant to the inquiry and provide clear, concise details for each item.
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150
    )

    return response['choices'][0]['message']['content'].strip()

if __name__ == "__main__":
    while True:
        client_query = input("Enter your query about clothing: ")

        if client_query.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        suggestions = suggest_clothes(client_query, products)

        print("\nAI Suggestions:")
        print(suggestions)
        print("\n" + "="*50 + "\n")
