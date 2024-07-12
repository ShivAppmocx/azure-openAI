# from dotenv import load_dotenv
import os
import openai

# load_dotenv()

openai.api_type = "azure"
# openai.api_base = "openai/deployments//subscriptions/9e4718ce-bdd1-450e-b4fa-f4b0e918fc7e/resourceGroups/Appmocx-Test-Server_group/providers/Microsoft.CognitiveServices/accounts/AI-Fab-RAG-Model/deployments/gpt-4inst2/chat/completions?api-version=2023-03-15-preview"

# openai.api_base = "https://ai-fab-rag-model.openai.azure.com/"
openai.api_base = "https://fabric-poc.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = os.getenv("OPENAI_API_KEY")
# openai.api_key = "7f3b4c1fca7e465f8a4f0b5a2c065113"

def get_completion_from_messages(system_message, user_message, model="gpt-4", temperature=0, max_tokens=500) -> str:

    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': f"{user_message}"}
    ]
    
    response = openai.ChatCompletion.create(
        engine=model,
        messages=messages,
        temperature=temperature, 
        max_tokens=max_tokens, 
    )
    
    return response.choices[0].message["content"]

if __name__ == "__main__":
    system_message = "You are a helpful assistant"
    user_message = "Hello, how are you?"
    print(get_completion_from_messages(system_message, user_message))
