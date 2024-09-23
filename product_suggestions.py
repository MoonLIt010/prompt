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
with open('structured_products_complete_v2.csv', 'r') as csv_file:
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
    You are an AI assistant for an online clothing store, specializing in fashion and clothing recommendations. You are fluent in both English and Arabic.

    Below is a list of products, each with its ID, name, description, category, style, season, and image folder.

    Product List:
    {product_list_str}

    A customer has submitted the following inquiry (which could be in English or Arabic): "{client_query}"

    Your task is to:

    1. **Understand the Inquiry**: Carefully read the customer's inquiry to understand their needs, preferences, and any specific items or outfits they mention.

    2. **Expert Selection**: As an expert in clothing and fashion, select the most appropriate products from the product list that match the customer's needs. This may include suggesting clothes, matching outfits, or recommending products based on outfits the customer has or has bought.

    3. **Language Processing**: If the inquiry is in Arabic, process it accordingly without any loss of meaning or context.

    4. **Response Format**: Provide **only** the IDs of the selected products, separated by commas if more than one. Do **not** include any additional text, explanations, or formatting.

    **Example**:

    - **Inquiry**: "I need a summer dress for a beach party."
    - **Response**: 101, 205

    Please provide only the IDs of the selected items in your response.
    """


    try:
        # Make API call to OpenAI GPT-4 using chat completion (new method in >=1.0.0)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            # model="gpt-4",
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
