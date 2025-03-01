import os
from groq import Groq

class GroqLLMClient:
    def __init__(self, api_key: str = None):
        """
        Initialize the Groq LLM client.

        Args:
            api_key (str, optional): Your Groq API key. If not provided, the client will
                                     attempt to retrieve it from the environment variable 'GROQ_API_KEY'.
        Raises:
            ValueError: If no API key is provided and the environment variable is not set.
        """
        if api_key is None:
            api_key = os.environ.get("GROQ_API_KEY")
            if not api_key:
                raise ValueError("API key must be provided or set in the environment variable 'GROQ_API_KEY'.")
        self.client = Groq(api_key=api_key)

    def chat_completion(self, prompt: str, model: str = "llama-3.3-70b-versatile", stream: bool = False) -> str:
        """
        Send a prompt to the Groq LLM and retrieve the response.

        Args:
            prompt (str): The prompt to send to the LLM.
            model (str, optional): The model identifier to use. Defaults to "llama-3.3-70b-versatile".
            stream (bool, optional): Whether to stream the response. Defaults to False.

        Returns:
            str: The content of the LLM's response.
        """
        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=model,
            stream=stream,
        )
        # Return the content of the first choice from the response.
        return response.choices[0].message.content

if __name__ == '__main__':
    # Example usage:
    groq_client = GroqLLMClient()
    prompt = "Explain the importance of fast language models"
    response = groq_client.chat_completion(prompt)
    print("LLM Response:")
    print(response)

