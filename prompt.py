import openai
import os
import re
import requests
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set the API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Define the FastAPI instance
app = FastAPI()

# Define the FastAPI endpoints for the product and evaluations data
PROJECTS_API_URL = "http://127.0.0.1:8000/projects"
EVALUATIONS_API_URL = "http://127.0.0.1:8000/evaluations"

# Pydantic model for the query input
class ClientQuery(BaseModel):
    query: str

# Function to fetch products from the API
def fetch_products():
    try:
        response = requests.get(PROJECTS_API_URL)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching products: {e}")
        return []

# Function to fetch evaluations from the API
def fetch_evaluations():
    try:
        response = requests.get(EVALUATIONS_API_URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching evaluations: {e}")
        return []

# Function to generate suggestions based on the client query
def generate_prompt(client_query, products, clients_data):
    product_list_str = ""
    for product in products:
        product_list_str += f"- ID: {product['id']}, Name: {product['name']}, Description: {product['description']}, " \
                            f"Category: {', '.join([category['en_name'] for category in product['categories']])}, " \
                            f"Price: {product['price']}, Times Purchased: {product['sold']}\n"

    # Prepare clients data string (adapting evaluations as client purchase history)
    clients_data_str = ""
    for client in clients_data:
        purchased_products_str = ""
        product = next((p for p in products if p['id'] == client['product_id']), None)
        if product:
            purchased_products_str += f"  - ID: {product['id']}, Name: {product['name']}, Description: {product['description']}, " \
                                      f"Category: {', '.join([category['en_name'] for category in product['categories']])}\n"
        clients_data_str += f"Client ID: {client['user_id']}\nPurchase History:\n{purchased_products_str}\n"

    # Check if the client query is for personalized suggestion
    personalized_suggestion = False
    client_name = ""
    trend_request = False

    # Regex patterns for matching client name with 'suggestion' or 'اقتراح'
    suggestion_pattern_en = r"^(.*)\s+suggestion$"
    suggestion_pattern_ar = r"^(.*)\s+اقتراح$"
    trend_pattern_en = r"^trends$"
    trend_pattern_ar = r"^شائع$"

    if re.match(suggestion_pattern_en, client_query, re.IGNORECASE):
        personalized_suggestion = True
        client_name = re.match(suggestion_pattern_en, client_query, re.IGNORECASE).group(1).strip()
    elif re.match(suggestion_pattern_ar, client_query, re.IGNORECASE):
        personalized_suggestion = True
        client_name = re.match(suggestion_pattern_ar, client_query, re.IGNORECASE).group(1).strip()
    elif re.match(trend_pattern_en, client_query, re.IGNORECASE) or re.match(trend_pattern_ar, client_query, re.IGNORECASE):
        trend_request = True

    # Construct the prompt
    if personalized_suggestion:
        prompt = f"""
You are an AI assistant for an online clothing store, specializing in fashion and clothing recommendations. You are fluent in both English and Arabic.

Below is a list of products, each with its ID, name, description, category, price, and times purchased.

Product List:
{product_list_str}

Also, here is data about clients' previous interactions and purchases:

{clients_data_str}

A customer named "{client_name}" has requested personalized suggestions based on their previous purchases.

Your task is to:

1. **Analyze Client's Purchase History**: Review the client's past purchases to understand their preferences in terms of style, color, category, and season.

2. **Expert Selection**: As an expert in clothing and fashion, select the most appropriate products from the product list that match the client's preferences. Suggest matching clothes and/or matching products and/or products with the same style, color, or taste as the ones the client used to purchase.

3. **Response Format**: Provide **only** the IDs of the selected products, separated by commas if more than one. Do **not** include any additional text, explanations, or formatting.

**Example**:

- **Response**: 101, 205

Please provide only the IDs of the selected items in your response.
"""
    elif trend_request:
        prompt = f"""
You are an AI assistant for an online clothing store, specializing in fashion and clothing recommendations. You are fluent in both English and Arabic.

Below is a list of products, each with its ID, name, description, category, price, and times purchased.

Product List:
{product_list_str}

A customer has requested suggestions for popular products that are trending now.

Your task is to:

1. **Select Popular Products**: From the product list, select the products that are most popular based on how many times they have been purchased by clients in general.

2. **Response Format**: Provide **only** the IDs of the selected products, separated by commas if more than one. Do **not** include any additional text, explanations, or formatting.

**Example**:

- **Response**: 101, 205

Please provide only the IDs of the selected items in your response.
"""
    else:
        # Original prompt
        prompt = f"""
You are an AI assistant for an online clothing store, specializing in fashion and clothing recommendations. You are fluent in both English and Arabic.

Below is a list of products, each with its ID, name, description, category, price, and times purchased.

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

    return prompt

# FastAPI route for generating product suggestions based on a query
@app.post("/suggest_clothes")
async def suggest_clothes(query: ClientQuery):
    # Fetch products and evaluations
    products = fetch_products()
    evaluations = fetch_evaluations()

    # Generate the OpenAI prompt
    prompt = generate_prompt(query.query, products, evaluations)

    try:
        # Make API call to OpenAI GPT-4 using chat completion
        response = openai.ChatCompletion.create(
            # model="gpt-3.5-turbo",
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant for an online clothing store."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )

        # Return the response from the AI (expected to be only IDs)
        return {"suggestions": response.choices[0].message["content"].strip()}

    except Exception as e:
        # Handle errors, such as API issues
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

