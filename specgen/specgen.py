import argparse
import os
import openai
import time
import signal
import sys
import subprocess

from chatgpt_wrapper import request_chatgpt_engine
from prompt_format import FORMAT_REFINE_PROMPT, WEAK_SPEC_ERR
from util import file2str, parse_code_from_reply

from generation_prompt import create_generation_prompt_config
from refinement_prompt import create_specialized_patcher_prompt_config, gen_extra_guidance, extract_err_type, append_failed_code_with_prompt

def extract_lineno_from_err_info(err_info):
    temp_list = []
    err_list = []
    err_info_list = err_info.split('\n')
    for line in err_info_list:
        if line.strip() == "^":
            err_list.append(temp_list)
            temp_list = []
        else:
            temp_list.append(line)
    lineno_list = []
    for err in err_list:
        lineno_list.append(int(err[0].split(":")[1]))
    return lineno_list

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException

signal.signal(signal.SIGALRM, timeout_handler)

def validate_openjml(opnejml_command, code_with_spec, classname):
    tmp_filename = os.path.abspath(".") + "/tmp/{filename}.java".format(filename=classname)
    tmp_file = open(tmp_filename, 'w')
    tmp_file.write(code_with_spec)
    tmp_file.close()
    cmd = opnejml_command + tmp_filename
    TIMEOUT = 0 # seconds
    signal.alarm(TIMEOUT)
    try:        
        res_lines = os.popen(cmd).readlines()
        signal.alarm(0)
    except TimeoutException:
        return "Timeout"
    res = ""
    for line in res_lines:
        res = res + line
    return res

def validate_openjml_equiv(completeness_equiv_flags, code_with_spec, classname):
    tmp_filename_code = os.path.abspath(".") + "/tmp/{filename}.java".format(filename=classname)
    with open(tmp_filename_code, 'w') as tmp_file:
        tmp_file.write(code_with_spec)

    tmp_filename_equiv_test = os.path.abspath(".") + "/tmp/{filename}_Test.java".format(filename=classname)

    try:
        equiv_result = subprocess.run(
            [
                "python3",
                "src/equivalence_check.py",
                tmp_filename_code,
                *completeness_equiv_flags.split(),
                "--to_file",
                tmp_filename_equiv_test,
            ],
            capture_output=True,
            text=True,
            timeout=120,   # seconds
            check=False,
        )
    except subprocess.TimeoutExpired:
        return "TIMEOUT"

    return "" if equiv_result.returncode == 0 else WEAK_SPEC_ERR

def mutate_token_list_random(token_list, has_forall, dont_mutate_logical):
    res_list = []
    token_variant_list = []
    if len(token_list) == 0:
        return [[""]]
    if token_list[0].find("\\forall") != -1 or token_list[0].find("\\exists") != -1:
        dont_mutate_logical = True
        tmp_str = token_list[0]
        token_variant_list.append(tmp_str.replace("forall", "exists"))
        token_variant_list.append(tmp_str.replace("exists", "forall"))
    elif token_list[0] == "&&" or token_list[0] == "||":
        if dont_mutate_logical:
            token_variant_list = [token_list[0]]
        else:
            token_variant_list = ["&&", "||"]
        if has_forall:
            dont_mutate_logical = False
    elif token_list[0] == "<=":
        token_variant_list = ["<", "<=", "- 1 <="]
    elif token_list[0] == ">=":
        token_variant_list = [">", ">=", "+ 1 >="]
    elif token_list[0] == "<":
        token_variant_list = ["<", "<="]
    elif token_list[0] == ">":
        token_variant_list = [">", ">="]
    elif not has_forall and (token_list[0] == "+" or token_list[0] == "-"):
        token_variant_list = ["+", "-"]
    else:
        token_variant_list = [token_list[0]]
    for variant in token_variant_list:
        for res in mutate_token_list_random(token_list[1:], has_forall, dont_mutate_logical):
            tmp_list = [variant]
            tmp_list.extend(res)
            res_list.append(tmp_list)
    return res_list

def spec_mutator_random(line):
    res_list = []
    has_forall = (line.find("forall") != -1 or line.find("exists") != -1)
    res_token_list_list = mutate_token_list_random(line.split(' '), has_forall, True)
    for token_list in res_token_list_list:
        tmp_str = ""
        for token in token_list:
            tmp_str = tmp_str + token + " "
        res_list.append(tmp_str)
    return res_list

def mutate_token_list_prior(token_list, current_index):
    res_list = []
    token_variant_list = []
    if current_index >= len(token_list):
        return [[""]]
    if token_list[current_index] == "<=":
        token_variant_list = ["<", "<=", "- 1 <="]
    elif token_list[current_index] == ">=":
        token_variant_list = [">", ">=", "+ 1 >="]
    elif token_list[current_index] == "<":
        token_variant_list = ["<", "<="]
    elif token_list[current_index] == ">":
        token_variant_list = [">", ">="]
    else:
        token_variant_list = [token_list[current_index]]
    for variant in token_variant_list:
        for res in mutate_token_list_prior(token_list, current_index + 1):
            tmp_list = [variant]
            tmp_list.extend(res)
            res_list.append(tmp_list)
    return res_list

def spec_mutator_heuristic(line):
    res_list = []
    has_forall = (line.find("forall") != -1 or line.find("exists") != -1)
    token_list = line.split(' ')
    res_token_list_list = mutate_token_list_prior(token_list, 0)
    for token_list in res_token_list_list:
        tmp_str = ""
        for token in token_list:
            tmp_str = tmp_str + token + " "
        res_list.append(tmp_str)

    res_list_random = spec_mutator_random(line)
    res_list_random_filtered = []
    for str1 in res_list_random:
        flag = False
        for str2 in res_list:
            if str1 == str2:
                flag = True
                break
        if not flag:
            res_list_random_filtered.append(str1)
    res_list.extend(res_list_random_filtered)
    return res_list
    

def is_invariant_or_postcondition(line):
    return line.find("@") != -1 and (line.find("invariant") != -1 or line.find("maintaining") != -1 or line.find("ensures") != -1 or line.find("decreases") != -1 or line.find("increases") != -1)

def is_assert(line):
    return line.find("@") != -1 and line.find("assert") != -1

def config2str(config):
    res = ""
    for message in config["messages"]:
        res += "{role}: {content}\n".format(role=message['role'], content=message['content'])
    return res

# Does not add newline automatically
def print_and_log(msg, log_file):
    print(msg, end = '')
    log_file.write(msg)

def print_and_log_config(config, log_file):
    msg = config2str(config) + "\n"
    print_and_log(msg, log_file)

def print_and_log_msg(message, log_file):
    msg = "{r}:{c}\n".format(r=message['role'], c=message['content'])
    print_and_log(msg, log_file)

def simple_tokenize_java(src: str):
    """
    Remove // and /* */ comments and split only on whitespace.
    Returns consecutive non-whitespace runs as tokens.
    Note: this does not handle things inside strings (but we do not have those in the dataset)
    """
    tokens = []
    cur = []
    i, n = 0, len(src)
    while i < n:
        ch = src[i]
        nxt = src[i + 1] if i + 1 < n else ''

        # line comment: //
        if ch == '/' and nxt == '/':
            if cur:
                tokens.append(''.join(cur)); cur = []
            i += 2
            while i < n and src[i] != '\n':
                i += 1
            continue

        # block comment: /* ... */
        if ch == '/' and nxt == '*':
            if cur:
                tokens.append(''.join(cur)); cur = []
            i += 2
            while i + 1 < n and not (src[i] == '*' and src[i + 1] == '/'):
                i += 1
            i = i + 2 if i + 1 < n else n
            continue

        # whitespace splits tokens
        if ch in (' ', '\t', '\r', '\n'):
            if cur:
                tokens.append(''.join(cur)); cur = []
            i += 1
            continue

        # accumulate non-whitespace chars
        cur.append(ch)
        i += 1

    if cur:
        tokens.append(''.join(cur))
    return tokens

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str)
    parser.add_argument("--key_file", type=str, default="api_key.txt")
    parser.add_argument("--max_gen_iterations", type=int, default=10)
    parser.add_argument("--model", choices=["gpt-3.5-turbo", "gpt-4.1-mini", "gpt-5-mini"], required=True)
    parser.add_argument("--prompt_type", choices=["original", "strict"], required=True)
    parser.add_argument("--mutation", action='store_true', default=False)
    parser.add_argument("--embedded_compl", action='store_true', default=False)
    parser.add_argument("--use_nonnull_and_no_ovf_asm", action='store_true', default=False)
    args = parser.parse_args()

    classname = args.input.split('/')[-1].split('.')[0]

    logs_dir = os.path.join(os.path.abspath("."), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    f_log = open(os.path.join(logs_dir, "log_{name}.txt".format(name=classname)), "w")

    if args.model == "gpt-3.5-turbo":
        model = "gpt-3.5-turbo-1106"
        temperature = 0.4
    elif args.model == "gpt-4.1-mini":
        model = "gpt-4.1-mini-2025-04-14"
        temperature = 0.4
    elif args.model == "gpt-5-mini":
        model = "gpt-5-mini-2025-08-07"
        temperature = 1.0 # reasoning model, only accepts 1
    else:
        print(f'Invalid model: {args.model}')
        exit(-1)

    # Note: this header was added after I'd run almost all experiments
    # I added when cleaning up the code and creating the documentation
    # That's why it's not in the (majority) of logs
    print_and_log(f'--input {args.input}\n'
                  f'--max_gen_iterations {args.max_gen_iterations}\n'
                  f'--model {model}\n'
                  f'--temperature {temperature}\n'
                  f'--prompt_type {args.prompt_type}\n'
                  f'--mutation {args.mutation}\n'
                  f'--embedded_compl {args.embedded_compl}\n'
                  f'--use_nonnull_and_no_ovf_asm {args.use_nonnull_and_no_ovf_asm}\n', f_log)

    if not os.access(args.input, os.R_OK):
        print("Cannot open input file {filename}".format(filename=args.input))
        exit(-1)

    openai.api_key = open(args.key_file, 'r').read().strip()
    input_code = file2str(args.input)
    original_code_tokens = simple_tokenize_java(input_code)

    # required for creating files to check with OpenJML
    tmp_dir = os.path.join(os.path.abspath("."), "tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    if args.use_nonnull_and_no_ovf_asm: # the setup from Ma et al. evaluation
        openjml_command = "openjml --esc --esc-max-warnings 1 --arithmetic-failure=quiet --nonnull-by-default --timeout 200 "
        completeness_equiv_flags = "-no_check_feas -no_check_arith -no_check_null"
    else:
        openjml_command = "openjml --esc --esc-max-warnings 1 --nullable-by-default --timeout 200 "
        completeness_equiv_flags = "-no_check_feas"

    num_verify = 0

    start_time = time.perf_counter()

    # Candidate Generation Phase
    print_and_log("=============== Generation Phase ===============\n", f_log)
    done_flag = False
    config = {}
    current_code = input_code.strip()
    err_info = ""
    err_types = []
    first_generation_message_length = 0
    for i in range(1, args.max_gen_iterations+1):
        if i == 1:
            # First gen: gets the prompt, few shots and task description. Appends LLM's return as the last message
            print_and_log("--------------- Iteration {num} ---------------\n".format(num=i), f_log)
            config = create_generation_prompt_config(model, temperature, args.prompt_type, input_code, classname)
            # in each attempt, we want to keep those and change the remaining
            first_generation_message_length = len(config['messages']) -1 #-1 : remove raw code
            print_and_log_config(config, f_log)
            ret = request_chatgpt_engine(config)
            print_and_log(f"assistant: {ret.choices[0].message.content}\n", f_log)
            parsed = parse_code_from_reply(ret.choices[0].message.content)
            if parsed is None:
                print_and_log("LLM gave up or generated incorrectly formatted code", f_log)
                err_info = "Gave up"
                break
            current_code = str(parsed).strip()
        else:
            err_types = extract_err_type(err_info)
            if len(err_types) != 0:
                # Failed gen, and we have guided feedback (examples regarding this specific failure).
                # Add feedback. Replace last attempt by (feedback + current failed code)
                print_and_log("--------------- Iteration {num} ---------------\n".format(num=i), f_log)
                create_specialized_patcher_prompt_config(config, first_generation_message_length, args.prompt_type, current_code, err_info)
                print_and_log_config(config, f_log)
                ret = request_chatgpt_engine(config)
                print_and_log(f"assistant: {ret.choices[0].message.content}\n", f_log)
                parsed = parse_code_from_reply(ret.choices[0].message.content)
                if parsed is None:
                    print_and_log("LLM gave up or generated incorrectly formatted code", f_log)
                    err_info = "Gave up"
                    break
                current_code = str(parsed).strip()
            elif not args.mutation or err_info.find("LoopInvariant") == -1 and err_info.find("Postcondition") == -1:
                # Failed gen, we do not have guided feedback, and it does not have mutation candidates (or mutation is disabled)
                # Replace last attempt by (fix instruction + current failed code)
                print_and_log("--------------- Iteration {num} ---------------\n".format(num=i), f_log)
                config['messages'] = config['messages'][0:first_generation_message_length]
                append_failed_code_with_prompt(config['messages'], args.prompt_type, current_code, err_info)
                
                print_and_log_config(config, f_log)
                ret = request_chatgpt_engine(config)
                print_and_log(f"assistant: {ret.choices[0].message.content}\n", f_log)

                parsed = parse_code_from_reply(ret.choices[0].message.content)
                if parsed is None:
                    print_and_log("LLM gave up or generated incorrectly formatted code", f_log)
                    err_info = "Gave up"
                    break
                current_code = str(parsed).strip()
            else:
                # Correct gen OR
                # Failed gen, we do not have guided feedback, and we do have mutation candidates (mutation is enabled)
                assert args.mutation
                done_flag = True # Skip to mutation phase/end
                break

        # handle other invalid generations:
        err_info = ""

        # gpt 3.5 turbo sometimes generates 'ensures \nothing' for behaviors that does not return or modify the input
        # For OpenJML 21-0-16, this causes a crash https://github.com/OpenJML/OpenJML/issues/899
        if 'ensures \\nothing' in current_code:
            err_info += "Error: \"ensures \\nothing\" is not valid grammar. If the behavior has no postconditions, you can leave it without an 'ensures' clause or do \"ensures true\"\n"
            err_types = []

        if 'requires \\nothing' in current_code:
            err_info += "Error: \"requires \\nothing\" is not valid grammar. If the behavior has no preconditions, you can leave it without an 'requires' clause or do \"requires true\"\n"
            err_types = []

        if 'assume' in current_code:
            err_info += "Error: you must NOT use assumptions. Please review your loop invariants or forbid all exception-causing states via preconditions ('requires' clause).\n"
            err_types = []

        if not "ensures" in current_code:
            err_info += "Error: You MUST add at least one postcondition (ensures). Consider adding more postconditions to strengthen your specification.\n"
            err_types = []

        if "signals" in current_code:
            err_info += "Error: You MUST NOT account for exceptional behavior. Forbid all exception-causing states via preconditions ('requires' clause).\n"
            err_types = []

        current_code_tokens = simple_tokenize_java(current_code)
        if original_code_tokens != current_code_tokens:
            err_info += "Error: You MUST NOT change the provided source code. Only add, remove or modify the JML specifications.\n"
            err_info += f"The original source code is\n```\n{input_code}\n```\n"
            err_types = []

        if err_info == "":
            err_info = validate_openjml(openjml_command, current_code, classname)
            num_verify = num_verify + 1
            err_types = extract_err_type(err_info)

        if err_info == "" and args.embedded_compl:
            # Valid code. Check if it is also 'complete'
            err_info = validate_openjml_equiv(completeness_equiv_flags, current_code, classname)
            err_types = []
            num_verify = num_verify + 1

        if err_info == "" or done_flag:
            break

        print_and_log(f"\n==== Gen Iteration finished with err_info ====\n{err_info}\n{46*'='}\n", f_log)

    # Gen phase is interrupted if it gets an error in postcondition or loop invariants
    # Mutation phase tries to fix these errors
    # If err_info is empty, it already succeeded in the gen phase and generated code accepted by the verifier
    if args.mutation and done_flag: # gen phase skippped because candidates were found
        # Mutation Phase
        print_and_log("=============== Mutation Phase ===============\n", f_log)
        current_code_list = current_code.split('\n')
        mutated_spec_list = []
        # Generate mutated spec set
        for index in range(len(current_code_list)):
            if is_invariant_or_postcondition(current_code_list[index]):
                for mutated_spec in spec_mutator_heuristic(current_code_list[index]):
                    mutated_spec_list.append({"content": mutated_spec, "index": index})
        i = 1
        while True: # exaustive: try ALL candidates
            if err_info == "":
                break

            print_and_log("--------------- Mutation Iteration {num} ---------------\n".format(num=i), f_log)
            if not is_invariant_or_postcondition(err_info):
                print_and_log("Unexpected verification error. Aborted.\n", f_log)
                break
            refuted_lineno_list = extract_lineno_from_err_info(err_info)
            # replace each error spec with mutated spec
            for lineno in refuted_lineno_list:
                index = lineno - 1
                if is_assert(current_code_list[index]):
                    current_code_list[index] = " "
                    continue
                if not is_invariant_or_postcondition(current_code_list[index]):
                    continue
                # Find mutated spec with same lineno
                found_flag = False
                for item in mutated_spec_list:
                    if item["index"] == index:
                        # replace error spec with mutated spec
                        current_code_list[index] = item['content']
                        mutated_spec_list.remove(item)
                        found_flag = True
                        break
                if not found_flag:
                    current_code_list[index] = " "
            current_code = ""
            for line in current_code_list:
                current_code = current_code + line + "\n"
            print_and_log(f"{current_code}", f_log)
            err_info = validate_openjml(openjml_command, current_code, classname)
            num_verify = num_verify + 1
            print_and_log(f"\n== Mut Iteration finished with err_info ==\n{err_info}\n{42*'='}\n", f_log)

            i += 1

    time_elapsed = int(time.perf_counter() - start_time)  # whole seconds (truncated)
    print_and_log("\nFinished. Verifier invoked {num} times\n".format(num=num_verify), f_log)
    print_and_log(f"--- Elapsed time: {time_elapsed} seconds ---\n", f_log)

    if err_info == "":
        print_and_log('Success', f_log) # we externally check if it's valid, complete or complete_gt
    else:
        print_and_log('Failure', f_log)

    f_log.close()

    if err_info == "":
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
