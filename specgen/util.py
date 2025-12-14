import os

def file2str(filename):
    res = ""
    with open(filename,"r") as f:
        for line in f.readlines():
            res = res + line
    return res

def parse_code_from_reply(content):
    # lines = content.split('\n')
    # res = ""
    # flag = False
    # for line in lines:
    #     if line.strip() == '```' and flag:
    #         break
    #     if flag:
    #         res = res + line + "\n"
    #     if line.strip() == '```' and not flag:
    #         flag = True
    # Sometimes the LLM gives up, and there is no code. Or unformatted output.
    # Either way should be considered a failure
    splitted = content.split("```")
    if len(splitted) < 2:
        return None
    extracted_str = splitted[1]
    extracted_str = extracted_str if not extracted_str.startswith('java') else extracted_str[len('java'):]
    return extracted_str