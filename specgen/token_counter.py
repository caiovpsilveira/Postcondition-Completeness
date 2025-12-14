import tiktoken

def count_str_token(model, string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def count_config_token(model, config) -> int:
    sum = 0
    for message in config['messages']:
        sum += count_str_token(model, message['content'])
    return sum