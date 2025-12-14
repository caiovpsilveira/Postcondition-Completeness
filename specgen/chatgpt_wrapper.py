import openai
import os
import signal
import time
from openai import AzureOpenAI
import httpx

def create_chatgpt_config(messages, model, temperature):
    config = {
        "model": model,
        "temperature": temperature,
        "messages": []
    }
    config["messages"] = messages
    return config

def handler(signum, frame):
    raise Exception("end of time")

def request_chatgpt_engine(config):
    ret = None
    while ret is None:
        try:
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(0)
            with open("./api_key.txt", 'r') as f:
                api_key = f.read().strip()
            client = openai.OpenAI(api_key=api_key)
            ret = client.chat.completions.create(
                model=config["model"],
                messages=config["messages"],
                temperature=config.get("temperature", 0.7)
            )
            signal.alarm(0)  # cancel alarm
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
