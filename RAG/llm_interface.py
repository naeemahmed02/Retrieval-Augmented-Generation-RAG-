from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import os

class LLMInterface:
    """
    A wrapper class to initialize and interact with a Google Generative AI LLM via LangChain.
    """

    def __init__(self, model_name: str, temperature: float = 0.7, api_key: str = None):
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError("Google API Key is missing.")

        self.llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=self.temperature,
            google_api_key=self.api_key
        )

    def chain(self, system_prompt: str, user_prompt: str):
        """
        Creates a LangChain runnable chain using the system and user prompts.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_prompt)
        ])
        return prompt | self.llm

    def run(self, system_prompt: str, user_prompt: str, input_values: dict):
        chain = self.chain(system_prompt, user_prompt)
        result = chain.invoke(input_values)
    
        # If result is a string
        if isinstance(result, str):
           return result

        # If result is LangChain's AIMessage
        if hasattr(result, "content"):
           return result.content

        # Fallback: Convert entire result to string
        return str(result)