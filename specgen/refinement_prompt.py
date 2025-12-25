import string

from prompt_format import FORMAT_ORIGINAL_REFINEMENT_PROMPT, FORMAT_STRICT_REFINEMENT_PROMPT
from util import file2str

def gen_extra_guidance(err_info):
    if err_info.find('visibility') != -1:
        return "To avoid errors related to visibility, you can add \"spec_public\" specifications to all the members (especially private ones) within the class."
    elif err_info.find('non-pure') != -1:
        return "To avoid errors related to non-pure methods, you can add \"pure\" specifications to the methods that doesn't modify any class members."
    elif err_info.find('NegativeIndex') != -1:
        return "The \"PossiblyNegativeIndex\" error indicates that the loop invariant is not restricting the possibility of a negative index in the array access. You should consider modifying corresponding \"loop_invariant\" or \"maintaining\" specifications."
    elif err_info.find('TooLargeIndex') != -1:
        return "The \"PossiblyTooLargeIndex\" error indicates that the loop invariant is allowing an outside of bounds access. You should consider modifying corresponding \"loop_invariant\" or \"maintaining\" specifications."
    elif err_info.find('ArithmeticOperationRange') != -1 and err_info.find('negation') != -1:
        return "To avoid integer overflow in integer negation operation, you can add a precondition (\"requires\") to propagate the requirement to the caller, to guarantee that the operation result is within expressable range (smaller than maximum value and bigger than minimum value)."
    elif err_info.find('overflow') != -1:
        return "To avoid integer overflow in arithmetic operation, you can add a precondition (\"requires\") to propagate the requirement to the caller, to guarantee that the operation result is within expressable range (smaller than maximum value and bigger than minimum value)."
    elif err_info.find('underflow') != -1:
        return "To avoid integer underflow in arithmetic operation, you can add a precondition (\"requires\") to propagate the requirement to the caller, to guarantee that the operation result is within expressable range (smaller than maximum value and bigger than minimum value)."
    elif err_info.find('LoopInvariantBeforeLoop') != -1:
        return "The \"LoopInvariantBeforeLoop\" error indicates that the loop invariant you stated may be violated before entering the loop. You should consider modifying corresponding \"loop_invariant\" or \"maintaining\" specifications."
    else:
        return ""

def read_refine_as_msg(prompt_type, dirname):
    dirpath = "specgen/prompts/refine/" + dirname + "/"
    original_code = file2str(dirpath + "original")
    err_info = file2str(dirpath + "err_info")
    refined_code = file2str(dirpath + "refined")

    if prompt_type == "original":
        prompt = FORMAT_ORIGINAL_REFINEMENT_PROMPT
    elif prompt_type == "strict":
        prompt = FORMAT_STRICT_REFINEMENT_PROMPT
    else:
        assert 0
        prompt = ""

    msg_request = {
        'role': 'user',
        'content': prompt.format(code=original_code, info=err_info)
    }
    msg_reply = {
        'role': 'assistant',
        'content': '```\n{code}\n```'.format(code=refined_code)
    }
    msg_request['content'] += gen_extra_guidance(err_info)
    return [msg_request, msg_reply]

def extract_err_type(err_info):
    prompt_list = []
    keyword_dict = {
        "DivideByZero": "divide_by_zero",
        "visibility": "private_visibility",
        "NegativeIndex": "negative_index",
        "TooLargeIndex": "too_large_index",
        "ArithmeticOperationRange negation": "overflow_negation",
        "overflow sum": "overflow_sum",
        "overflow difference": "overflow_sub",
        "overflow multiply": "overflow_mul",
        "overflow divide": "overflow_div",
        "underflow sum": "underflow_sum",
        "underflow difference": "underflow_sub",
        "underflow multiply": "underflow_mul",
        #"underflow divide": "underflow_div",
    }
    for key in keyword_dict:
        keyword_list = key.split(' ')
        flag_all_in = True
        for keyword in keyword_list:
            if err_info.find(keyword) == -1:
                flag_all_in = False
                break
        if flag_all_in:
            prompt_list.append(keyword_dict[key])
    return prompt_list

def append_failed_code_with_prompt(msg_list, prompt_type, current_code, err_info):
    if prompt_type == "original":
        prompt = FORMAT_ORIGINAL_REFINEMENT_PROMPT
    elif prompt_type == "strict":
        prompt = FORMAT_STRICT_REFINEMENT_PROMPT
    else:
        assert 0
        prompt = ""

    msg_request = {
        'role': 'user',
        'content': prompt.format(code=current_code, info=err_info)
    }
    msg_request['content'] += gen_extra_guidance(err_info)
    msg_list.append(msg_request)

def create_specialized_patcher_prompt_config(config, original_config_length, prompt_type, current_code, err_info):
    messages = []

    prompt_list = extract_err_type(err_info)
    for dirname in prompt_list:
        messages.extend(read_refine_as_msg(prompt_type, dirname))

    append_failed_code_with_prompt(messages, prompt_type, current_code, err_info)

    assert original_config_length != 0
    config['messages'] = config['messages'][0:original_config_length]
    config['messages'].extend(messages)
