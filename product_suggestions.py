import openai
import os
from dotenv import load_dotenv
import data

# Load environment variables from .env file
load_dotenv()

# Retrieve the OpenAI API key from the environment
openai.api_key = os.getenv('OPENAI_API_KEY')

def suggest_clothes(client_query, products):
    prompt = f"""
    You are an AI assistant for an online clothing store. Below is a list of products, each with its name, description, category, style, season, and image folder.

    Product List:
    {products}

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

    # Call GPT-3.5 Turbo as an alternative
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150
    )

    return response['choices'][0]['message']['content'].strip()

# Main loop to interact with the user
if __name__ == "__main__":
    while True:
        # Prompt the user for a query
        client_query = input("Enter your query about clothing: ")

        if client_query.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        # Get suggestions from the AI
        suggestions = suggest_clothes(client_query, data.products)

        # Display the AI's suggestions
        print("\nAI Suggestions:")
        print(suggestions)
        print("\n" + "="*50 + "\n")
