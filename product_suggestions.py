import openai
import os
import csv
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set the API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Load products from CSV file
products = []
with open('structured_products.csv', 'r') as csv_file:
    reader = csv.DictReader(csv_file)  # This reads each row as a dictionary
    for row in reader:
        # Ensure necessary fields exist and assign default values if missing
        product = {
            'id': row.get('id'),
            'name': row.get('name'),
            'description': row.get('description'),
            'category': row.get('category'),
            'style': row.get('style'),
            'season': row.get('season')
        }
        products.append(product)

# Function to suggest clothes based on client query
def suggest_clothes(client_query, products):
    product_list_str = ""
    for product in products:
        product_list_str += f"- ID: {product['id']}, Name: {product['name']}, Description: {product['description']}, " \
                            f"Category: {product['category']}, Style: {product['style']}, " \
                            f"Season: {product['season']}\n"

    # Construct the prompt
    prompt = f"""
    You are an AI assistant for an online clothing store. Below is a list of products, each with its ID, name, description, category, style, season, and image folder.

    Product List:
    {product_list_str}

    A customer has submitted the following inquiry: "{client_query}"

    Your task:
    1. Review the provided inquiry carefully.
    2. Select the most appropriate clothing items from the product list based on the client's needs.
    3. Return only the IDs of the selected items.
    """

    try:
        # Make API call to OpenAI GPT-4 using chat completion (new method in >=1.0.0)
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant for an online clothing store."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )

        # Return the response from the AI (expected to be only IDs)
        return response.choices[0].message["content"].strip()


    except Exception as e:
        # Handle errors, such as API issues
        return f"Error: {str(e)}"

# Main loop to interact with the user
if __name__ == "__main__":
    while True:
        client_query = input("Enter your query about clothing: ")

        # Exit condition
        if client_query.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        # Get suggestions from the AI
        suggestions = suggest_clothes(client_query, products)

        # Display suggestions (IDs only)
        print("\nAI Suggestions (IDs only):")
        print(suggestions)
        print("\n" + "="*50 + "\n")
