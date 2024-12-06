import os
import time
from openai import OpenAI

# Initialize the OpenAI client with the provided API key and base URL.
client = OpenAI(
    api_key="",  # API key should be set here
    base_url=""  # The base URL for the API should be set here
)

def request_gpt_chat(prompt, model="gpt-3.5-turbo", retries=30):
    """
    Send a request to the GPT model for generating chat completions.

    Parameters:
    - prompt (str): The input prompt for GPT.
    - model (str): The model to be used, default is "gpt-3.5-turbo".
    - retries (int): Number of retries in case of failure, default is 30.

    Returns:
    - str: The generated answer from GPT or error message.
    """
    e = None
    for attempt in range(retries):
        try:
            # Call the GPT API for chat completions
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],  # Pass the user prompt
                temperature=0.7  # Control the randomness of the model's responses
            )

            # Extract and return the answer from the response
            answer = response.choices[0].message.content
            return answer

        except Exception as error:
            e = error
            print(f"Error calling GPT API: {e}, sleeping for 1 second before retrying...")  # Print error message
            time.sleep(1)  # Sleep for 1 second before retrying
            if "This model's maximum context length is 16385 tokens." in str(e):
                # If the error is due to the token limit, break out of the loop
                break

    print("Max retries exceeded.")
    return f"Error calling GPT API: {e}"  # Return error message if retries are exhausted

def request_gpt_embedding(input, retries=5):
    """
    Send a request to the GPT model to generate embeddings for the given input text.

    Parameters:
    - input (str): The input text to generate embeddings for.
    - retries (int): Number of retries in case of failure, default is 5.

    Returns:
    - list: The generated embedding vector or None if failed.
    """
    for attempt in range(retries):
        try:
            # Call the GPT API for embeddings
            response = client.embeddings.create(
                input=input,
                model="text-embedding-3-small"  # Specify the model for embeddings
            )

            # Extract the embedding vector from the response
            embedding = response.data[0].embedding
            time.sleep(0.1)  # Sleep briefly to avoid rate-limiting issues

            return embedding

        except Exception as e:
            if "Error code: 429" in str(e):
                # If rate limit exceeded, wait for 1 second before retrying
                print(f"Received 429 error, {e}, sleeping for 1 second before retrying...")
                time.sleep(1)
            else:
                print(f"Error calling GPT API: {e}")  # Print any other errors
                return None

    print("Max retries exceeded.")
    return None  # Return None if retries are exhausted
