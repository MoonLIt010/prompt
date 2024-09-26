# import openai
# import os
# import csv
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# # Set the API key
# openai.api_key = os.getenv('OPENAI_API_KEY')

# # Load products from CSV file
# products = []
# with open('structured_products_complete_v2.csv', 'r') as csv_file:
#     reader = csv.DictReader(csv_file)  # This reads each row as a dictionary
#     for row in reader:
#         # Ensure necessary fields exist and assign default values if missing
#         product = {
#             'id': row.get('id'),
#             'name': row.get('name'),
#             'description': row.get('description'),
#             'category': row.get('category'),
#             'style': row.get('style'),
#             'season': row.get('season')
#         }
#         products.append(product)

# # Function to suggest clothes based on client query
# def suggest_clothes(client_query, products):
#     product_list_str = ""
#     for product in products:
#         product_list_str += f"- ID: {product['id']}, Name: {product['name']}, Description: {product['description']}, " \
#                             f"Category: {product['category']}, Style: {product['style']}, " \
#                             f"Season: {product['season']}\n"

#     # Construct the prompt
#     prompt = f"""
#     You are an AI assistant for an online clothing store, specializing in fashion and clothing recommendations. You are fluent in both English and Arabic.

#     Below is a list of products, each with its ID, name, description, category, style, season, and image folder.

#     Product List:
#     {product_list_str}

#     A customer has submitted the following inquiry (which could be in English or Arabic): "{client_query}"

#     Your task is to:

#     1. **Understand the Inquiry**: Carefully read the customer's inquiry to understand their needs, preferences, and any specific items or outfits they mention.

#     2. **Expert Selection**: As an expert in clothing and fashion, select the most appropriate products from the product list that match the customer's needs. This may include suggesting clothes, matching outfits, or recommending products based on outfits the customer has or has bought.

#     3. **Language Processing**: If the inquiry is in Arabic, process it accordingly without any loss of meaning or context.

#     4. **Response Format**: Provide **only** the IDs of the selected products, separated by commas if more than one. Do **not** include any additional text, explanations, or formatting.

#     **Example**:

#     - **Inquiry**: "I need a summer dress for a beach party."
#     - **Response**: 101, 205

#     Please provide only the IDs of the selected items in your response.
#     """


#     try:
#         # Make API call to OpenAI GPT-4 using chat completion (new method in >=1.0.0)
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             # model="gpt-4",
#             messages=[
#                 {"role": "system", "content": "You are an AI assistant for an online clothing store."},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=1000
#         )

#         # Return the response from the AI (expected to be only IDs)
#         return response.choices[0].message["content"].strip()


#     except Exception as e:
#         # Handle errors, such as API issues
#         return f"Error: {str(e)}"

# # Main loop to interact with the user
# if __name__ == "__main__":
#     while True:
#         client_query = input("Enter your query about clothing: ")

#         # Exit condition
#         if client_query.lower() in ["exit", "quit"]:
#             print("Goodbye!")
#             break

#         # Get suggestions from the AI
#         suggestions = suggest_clothes(client_query, products)

#         # Display suggestions (IDs only)
#         print("\nAI Suggestions (IDs only):")
#         print(suggestions)
#         print("\n" + "="*50 + "\n")







import openai
import os
import csv
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set the API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Load products from CSV file
products = []
with open('structured_products_complete_v2.csv', 'r') as csv_file:
    reader = csv.DictReader(csv_file)  # Reads each row as a dictionary
    for row in reader:
        # Ensure necessary fields exist and assign default values if missing
        product = {
            'id': row.get('id'),
            'name': row.get('name'),
            'description': row.get('description'),
            'category': row.get('category'),
            'style': row.get('style'),
            'season': row.get('season'),
            'times_purchased': int(row.get('times_purchased', '0'))  # Assuming 'times_purchased' field exists
        }
        products.append(product)

# Load clients data from CSV file
clients_data = []
with open('client_data.csv', 'r') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        purchase_history_str = row.get('purchase_history', '')
        # Parse the purchase history into a list of product IDs
        purchase_history = [pid.strip() for pid in purchase_history_str.split(',') if pid.strip()]
        client = {
            'name': row.get('client_name'),
            'purchase_history': purchase_history  # This is a list of product IDs
        }
        clients_data.append(client)

# Function to suggest clothes based on client query
def suggest_clothes(client_query, products, clients_data):
    product_list_str = ""
    for product in products:
        product_list_str += f"- ID: {product['id']}, Name: {product['name']}, Description: {product['description']}, " \
                            f"Category: {product['category']}, Style: {product['style']}, " \
                            f"Season: {product['season']}, Times Purchased: {product['times_purchased']}\n"

    # Prepare clients data string
    clients_data_str = ""
    for client in clients_data:
        purchased_products_str = ""
        for pid in client['purchase_history']:
            # Find the product with the matching ID
            product = next((p for p in products if p['id'] == pid), None)
            if product:
                purchased_products_str += f"  - ID: {product['id']}, Name: {product['name']}, Description: {product['description']}, " \
                                          f"Category: {product['category']}, Style: {product['style']}, Season: {product['season']}\n"
        clients_data_str += f"Client Name: {client['name']}\nPurchase History:\n{purchased_products_str}\n"

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

Below is a list of products, each with its ID, name, description, category, style, season, and times purchased.

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

Below is a list of products, each with its ID, name, description, category, style, season, and times purchased.

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

Below is a list of products, each with its ID, name, description, category, style, season, and times purchased.

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
        # Make API call to OpenAI GPT-4 using chat completion
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
        suggestions = suggest_clothes(client_query, products, clients_data)

        # Display suggestions (IDs only)
        print("\nAI Suggestions (IDs only):")
        print(suggestions)
        print("\n" + "="*50 + "\n")
