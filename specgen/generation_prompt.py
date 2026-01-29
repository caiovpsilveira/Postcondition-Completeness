import random

from chatgpt_wrapper import create_chatgpt_config
from prompt_format import FORMAT_ORIGINAL_GENERATION_PROMPT, FORMAT_STRICT_GENERATION_PROMPT
from util import file2str

def read_oracle_as_msg(classname, prompt_type):
    filename_oracle = "./dataset_v1_annotated/" + classname + ".java"
    filename_clean = "./dataset_v1_no_annotations/" + classname + ".java"

    fmt = FORMAT_ORIGINAL_GENERATION_PROMPT if prompt_type == "original" else FORMAT_STRICT_GENERATION_PROMPT
    content_user = fmt.format(src_code=file2str(filename_clean))

    msg_request = {
        'role': 'user',
        'content': content_user
    }
    msg_reply = {
        'role': 'assistant',
        'content': '```\n{code}\n```'.format(code=file2str(filename_oracle))
    }
    return [msg_request, msg_reply]

def randomly_select_prompt(oracle_list, num, class_name):
    selected_list = random.sample(oracle_list, num)
    while(class_name in selected_list):
        selected_list.remove(class_name)
        selected_list.append(random.choice(oracle_list))
    return selected_list

def manually_select_prompt():
    return ["Neg", "BinarySearch", "BubbleSort", "Calculator", "CopyArray"]

def create_generation_prompt_config(model, temperature, prompt_type, input_code, class_name):
    msg_base = {
        'role': 'system',
        'content': 'You are a JML specification generator for java programs.'
    }
    messages = [msg_base]

    # few_shot_examples = set(["Abs1", "Abs2", "Add", "AllDigits", "ArrayAppend", "Avg1", "Avg2",
    #                "Calculator1", "Calculator2", "Clamp", "CompareArray", "ConvertTemperature",
    #                "CopyArray", "DivArrayByTwo", "DoubleArrayElements", "Find", "IsCommonFactor",
    #                "IsCommonMultiple", "IsPalindrome", "IsPrefix", "IsReverseArray",
    #                "IsStrictlyDecreasing", "IsStrictlyMonotonic", "LeapYear", "Max", "Min", "Mul",
    #                "ReverseArray", "SafeSum", "Swap1", "Swap2", "TwoSum"])

    # # create groups of closely related methods, to avoid giving them as examples
    # closely_related = []
    # closely_related.append(set(["Add1", "Add2"]))
    # closely_related.append(set(["Avg1", "Avg2"]))
    # closely_related.append(set(["Calculator1", "Calculator2"]))
    # closely_related.append(set(["IsCommonFactor", "IsCommonMultiple"]))
    # closely_related.append(set(["DivArrayByTwo", "DoubleArrayElements"]))
    # closely_related.append(set(["IsStrictlyDecreasing", "IsStrictlyMonotonic"]))
    # closely_related.append(set(["Max", "Min"]))
    # closely_related.append(set(["Add", "Mul"]))
    # closely_related.append(set(["ReverseArray", "IsReverseArray"]))
    # closely_related.append(set(["Swap1", "Swap2"]))

    # MODIFIED: for less variability, use the same few shot examples, instead of randomly sampling.
    # Since the examples are still in the dataset, need to remove them if they are the source code tasked.
    # Do not replace one example by another one with a very simmilar task

    few_shot_examples = ["easy/Abs1", "medium/DivArrayByTwo", "medium/IsPrefix", "medium/Find"]
    if class_name == 'Abs1': # Example with arithmetic failure if not considered
        few_shot_examples[0] = "easy/Avg1"
    elif class_name == 'DivArrayByTwo': # Example that modifies the array
        few_shot_examples[1] = 'medium/ReverseArray'
    elif class_name == 'IsPrefix': # Example with behaviors
        few_shot_examples[2] = 'medium/IsReverseArray'
    elif class_name == 'Find': # Example of 'order relevant in result'
        few_shot_examples[3] = 'medium/Min'

    #prompt_list = randomly_select_prompt(list(few_shot_examples), 3, class_name)
    # prompt_list = manually_select_prompt()
    for oracle in few_shot_examples:
        messages.extend(read_oracle_as_msg(oracle, prompt_type))

    if prompt_type == "original":
        prompt = FORMAT_ORIGINAL_GENERATION_PROMPT
    elif prompt_type == "strict":
        prompt = FORMAT_STRICT_GENERATION_PROMPT
    else:
        assert 0
        prompt = ""

    msg_request = {
        'role': 'user',
        'content': prompt.format(src_code=input_code)
    }
    messages.append(msg_request)
    return create_chatgpt_config(messages, model, temperature)
