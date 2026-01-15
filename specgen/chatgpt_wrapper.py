import openai
import os
import signal
import time

def create_chatgpt_config(messages, model, temperature):
    config = {
        "model": model,
        "temperature": temperature,
        "messages": []
    }
    config["messages"] = messages
    return config

def request_chatgpt_engine(config):
    ret = None
    while ret is None:
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                with open("./api_key.txt", "r") as f:
                    api_key = f.read().strip()
            client = openai.OpenAI(api_key=api_key)
            ret = client.chat.completions.create(
                model=config["model"],
                messages=config["messages"],
                temperature=config["temperature"]
            )
        except openai.BadRequestError as e:
            print(e)
            signal.alarm(0)
        except openai.RateLimitError as e:
            print("Rate limit exceeded. Waiting...")
            print(e)
            signal.alarm(0)
            time.sleep(5)
        except openai.APIConnectionError as e:
            print("API connection error. Waiting...")
            signal.alarm(0)
            time.sleep(5)
        except Exception as e:
            print(e)
            print("Unknown error. Waiting...")
            signal.alarm(0)
            time.sleep(1)
    return ret
