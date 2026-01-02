# This is a very simple file processor, that does not account for every construct of the JML language,
# but rather a subset that is present in both SpecGenBench-Annotated and SpecGenBench-result.
# Parses multiple methods in a Java class, extracting the signature, body and behaviors

# main method is "process_file", which returns a list of MethodSpecification

# A MethodSpecification has the method signature, the body (which includes loop invariants and local asserts),
# and a list of behaviors.
# A method may have multiple behaviors, separated by the "also" clause.
# In each behavior, annotations with "require" are classified as preconditions,
# and annotations with "assigns" and "ensures" are classified as postconditions.

import re
import argparse

# returs [method_name, method_args_decl, method_return_type, method_uniq_signature]
def process_method_signature(full_signature: str):
    # Remove possible annotations and modifiers except return type
    # Example: "public static int   add(int a, int b) {"
    # Goal: "int add(int, int)"
    # Some tests have more than one method per test, and some with method name overloading

    sig_pattern = re.compile(
        r'^(?:public|protected|private|static|final|synchronized|abstract|native|transient|volatile|\s)*'  # modifiers
        r'(?P<ret_type>[\w<>\[\],\s]+?)\s+'  # return type
        r'(?P<name>\w+)\s*'                  # method name
        r'\((?P<args>[^\)]*)\)'              # arguments
    )
    match = sig_pattern.match(full_signature.strip())
    if not match:
        assert 0
        return "unknown", "", "", full_signature.strip()  # fallback: return as is

    ret_type = ' '.join(match.group('ret_type').split())
    method_name = match.group('name').strip()
    args_decl = match.group('args').strip()
    arg_types = []
    arg_names = []
    if args_decl:
        # Only keep the type part of each argument
        for arg in args_decl.split(','):
            arg = arg.strip()
            if not arg:
                continue
            # Remove annotations and final keyword
            arg = re.sub(r'@\w+\s*', '', arg)
            arg = re.sub(r'\bfinal\b\s*', '', arg)
            # Take everything except the last word (which is the variable name)
            parts = arg.split()
            if len(parts) > 1:
                arg_type = ' '.join(parts[:-1]).strip()
                arg_names.append(parts[-1].strip())
            else:
                arg_type = parts[0].strip()

            arg_types.append(arg_type)
        signature = f"{ret_type} {method_name}({', '.join(arg_types)})"
    else:
        signature = f"{ret_type} {method_name}()"

    return method_name, args_decl, ret_type, signature

class Behavior:
    def __init__(self, preconditions: list[str], postconditions: list[str]) -> None:
        self.preconditions = preconditions
        self.postconditions = postconditions

class MethodSpecification:
    def __init__(self, name: str, is_model: bool, uniq_signature: str, args_decl: str, return_type: str, is_fresh_return: bool, behaviors: list[Behavior],
                 extra_qualifiers: list[str], body: str) -> None:
        self.name = name
        self.is_model = is_model
        self.uniq_signature = uniq_signature
        self.args_decl = args_decl
        self.return_type = return_type
        self.is_fresh_return = is_fresh_return
        self.behaviors = behaviors
        self.extra_qualifiers = extra_qualifiers
        self.body = body # includes the full signature

    def replace_method_calls(self, old_call: str, new_call: str) -> None:
        for behavior in self.behaviors:
            for i, pre in enumerate(behavior.preconditions):
                behavior.preconditions[i] = pre.replace(old_call + '(', new_call + '(')
            for i, pos in enumerate(behavior.postconditions):
                behavior.postconditions[i] = pos.replace(old_call, new_call)
        self.body = self.body.replace(old_call + '(', new_call + '(')

    def args_use(self) -> str:
        arg_names = []
        args = self.args_decl.split(",")
        for arg_decl in args:
            name = arg_decl.strip().split(" ")[1]
            arg_names.append(name)
        return ",".join(arg_names)

    def unify_preconditions(self) -> str:
        unified = ""
        for i, behavior in enumerate(self.behaviors):
            for precondition in behavior.preconditions:
                unified += precondition + "\n"
            if i + 1 < len(self.behaviors):
                unified += "//@ also\n"
        return unified
    
    def reconstruct_spec(self) -> str:
        unified = ""
        for i, behavior in enumerate(self.behaviors):
            for precondition in behavior.preconditions:
                unified += precondition + "\n"
            for postcondition in behavior.postconditions:
                unified += postcondition + "\n"
            if i + 1 < len(self.behaviors):
                unified += "//@ also\n"
        for extra in self.extra_qualifiers:
            unified += extra + "\n"
        return unified

    def __str__(self) -> str:
        ret = f"Name: {self.name}\n"
        ret += f"Signature: {self.uniq_signature}\n"
        ret += f"Args decl: {self.args_decl}\n"
        ret += f"Args use: {self.args_use()}\n"
        ret += f"Return type: {self.return_type}\n"
        ret += f"Extra qualifiers: {self.extra_qualifiers}\n"
        ret += f'Is model: {self.is_model}\n'
        for i, beh in enumerate(self.behaviors):
            ret += f"  Behavior {i+1}:\n"
            ret += f"    Preconditions: {beh.preconditions}\n"
            ret += f"    Postconditions: {beh.postconditions}\n"
        ret += "  Body:\n"
        ret += self.body
        return ret

# preprocess source code:
# make multiline comments /*@/ a single line //@
# make comments that split specs into multiple lines in a single line
def preprocess_transform_source_code(source_code: str):
    """
    Normalize JML in a Java source to a simple, line-oriented format so downstream code
    can parse it without a full JML parser.

    What it does:
    - Converts JML block comments (/*@ ... @*/) into standalone single-line //@ annotations,
      preserving indentation.
    - Extracts inline //@ annotations from code lines and emits them as their own lines,
      removing them from the code line to avoid mixing code and specs.
    - Coalesces multi-line/spec-fragment //@ annotations into a single line until a clause
      boundary (e.g., requires/ensures/assigns/modifies/loop_invariant/etc.) or a semicolon.
    - Treats 'pure', 'strictly_pure', 'spec_pure', and 'no_state' as signature modifiers:
      if they appear inside the method signature (even within /*@ ... @*/), they are emitted
      as a standalone //@ line immediately before the signature and never inside the body.
    - Avoids inserting extra blank lines by not emitting whitespace-only prefixes.

    Why:
    - The rest of this tool (e.g., extract_annotations) assumes all JML annotations start
      with //@ and fit on a single line. Normalizing here makes regex-based extraction
      robust across inputs (SpecGenBench-Annotated and result logs) without implementing
      a full JML parser.

    Returns:
    - The transformed source string with normalized //@ annotations.
    """

    splitted = source_code.splitlines()

    # First pass: normalize to single-line JML annotations starting with "//@"
    # - Convert /*@ ... @*/ blocks into one or more "//@" lines
    # - Extract inline "//@" to its own line (remove from code line)
    out_lines: list[str] = []
    inside_block = False
    block_indent = ""

    # Special JML modifiers that can appear inside method signatures
    special_modifiers = {"pure", "strictly_pure", "spec_pure", "no_state"}

    def clean_block_content(s: str) -> str:
        # Trim and remove leading '*' or '@' decorations and trailing '@'
        s = s.strip()
        s = re.sub(r'^\s*[@*]+\s*', '', s)
        s = re.sub(r'\s*[@*]+\s*$', '', s)
        # Collapse internal whitespace
        s = re.sub(r'\s+', ' ', s)
        return s

    for original_line in splitted:
        line = original_line

        # Track whether we just emitted code before a JML block on this same physical line
        prev_was_code_prefix = False
        line_leading_indent = re.match(r'^\s*', original_line).group(0)

        carry = line
        while carry is not None:
            if not inside_block:
                idx_block = carry.find("/*@")
                idx_single = carry.find("//@")

                # No JML comments in the remaining piece
                if idx_block == -1 and idx_single == -1:
                    # emit as-is
                    out_lines.append(carry)
                    carry = None
                    continue

                # Choose the earliest comment start
                idxs = [x for x in (idx_block, idx_single) if x != -1]
                start = min(idxs)

                # Text before the comment
                prefix = carry[:start]
                indent_for_jml = ""
                if prefix:
                    if prefix.strip() == "":
                        # whitespace-only: keep as indentation for the JML line, don't emit a blank line
                        indent_for_jml = prefix
                        prev_was_code_prefix = False
                    else:
                        # real code before comment: emit it (trim trailing spaces)
                        out_lines.append(prefix.rstrip())
                        prev_was_code_prefix = True

                if start == idx_single:
                    # Single-line JML comment: extract the content to its own line
                    jml_content = carry[start + 3:]  # skip "//@"
                    jml_content = jml_content.lstrip()
                    jml_line = ("//@ " + jml_content) if jml_content else "//@"
                    # Indent using indent_for_jml if available, otherwise keep original line indent
                    jml_indent = indent_for_jml if indent_for_jml != "" else line_leading_indent
                    out_lines.append(jml_indent + jml_line)
                    # Nothing after a single-line comment
                    carry = None
                else:
                    # Enter block JML comment
                    inside_block = True
                    # Prefer whitespace indentation if present, otherwise use the line's leading indent
                    block_indent = indent_for_jml if indent_for_jml != "" else line_leading_indent
                    # Advance past "/*@"
                    carry = carry[start + 3:]
            else:
                # Inside a JML block until "*/"
                end_idx = carry.find("*/")
                if end_idx == -1:
                    # Entire remainder is inside the block
                    content = clean_block_content(carry)
                    if content:
                        out_lines.append(block_indent + "//@ " + content)
                    # Continue to next physical line
                    carry = None
                else:
                    # There is block end on this same segment
                    raw_content = carry[:end_idx]
                    content = clean_block_content(raw_content)

                    # Suffix after the block
                    suffix = carry[end_idx + 2:]

                    if content:
                        # Check if this block is just a special modifier (e.g., pure)
                        if re.search(r'\b(pure|strictly_pure|spec_pure|no_state)\b', content):
                            modifier_line = block_indent + "//@ " + content
                            if prev_was_code_prefix and len(out_lines) >= 1 and not out_lines[-1].lstrip().startswith("//@"):
                                # Insert modifier BEFORE the signature/code line we just emitted,
                                # then merge the suffix into that same signature line to keep it on one line.
                                insert_at = len(out_lines) - 1
                                out_lines.insert(insert_at, modifier_line)
                                if suffix.strip():
                                    out_lines[-1] = out_lines[-1].rstrip() + " " + suffix.lstrip()
                                carry = None
                            else:
                                # No code before on this line; emit modifier now, then process suffix normally
                                out_lines.append(modifier_line)
                                carry = suffix if suffix != "" else None
                        else:
                            # Regular JML block -> emit as //@
                            out_lines.append(block_indent + "//@ " + content)
                            # Continue with suffix
                            carry = suffix if suffix != "" else None
                    else:
                        # Empty content; just continue with suffix
                        carry = suffix if suffix != "" else None

                    # Exit block
                    inside_block = False
                    block_indent = ""
                    # Reset prefix flag for subsequent segments on the same physical line
                    prev_was_code_prefix = False

    # Second pass: join split //@ lines into a single line where applicable
    # Heuristic: start new line when a new clause keyword starts, or previous line ended with ';'
    clause_starts = (
        "also",
        "requires",
        "ensures",
        "assigns",
        "assume",
        "assert",
        "maintaining",
        "loop_invariant",
        "loop_writes",
        "assigning",
        "loop_modifies",
        "modifies",
        "decreases",
        "measured_by",
        "pure",
        "spec_pure",
        "no_state",
        "strictly_pure",
        "model",
        "behaviors",
        "signals",
        "signals_only",
        "ghost",
    )

    # Precompile: clause keyword as a whole word at the beginning (after optional whitespace).
    _clause_start_re = re.compile(r"^\s*(?:" + "|".join(re.escape(k) for k in clause_starts) + r")\b", re.IGNORECASE)

    def is_clause_start(s: str) -> bool:
        return _clause_start_re.match(s) is not None

    _quantifier_re = re.compile(r"\\(forall|exists)\b")

    def looks_like_quantifier_header(s: str) -> bool:
        """
        Quantifiers often use semicolons to separate binder/range/predicate:
          \\forall int i; 0 <= i < n; P(i)
        Those semicolons should NOT force a flush/annotation split.
        """
        return _quantifier_re.search(s) is not None

    def ends_clause(s: str) -> bool:
        """
        Treat a trailing ';' as an end-of-annotation only if it *really* ends the line
        (ignoring trailing whitespace) and we are not in a quantifier header-ish construct.
        """
        s2 = s.rstrip()
        return s2.endswith(";") and not looks_like_quantifier_header(s2)

    joined: list[str] = []
    buffer_content: str | None = None
    buffer_indent: str = ""

    for line in out_lines:
        m = re.match(r'^(\s*)//@\s?(.*)$', line)
        if m:
            indent = m.group(1)
            content = m.group(2).strip()
            if buffer_content is None:
                buffer_content = content
                buffer_indent = indent
            else:
                # Start a new annotation line if the new content starts a new clause,
                # or if the previous buffered content truly ended a clause.
                if is_clause_start(content) or ends_clause(buffer_content):
                    joined.append(f"{buffer_indent}//@ {buffer_content}")
                    buffer_content = content
                    buffer_indent = indent
                else:
                    buffer_content = buffer_content + " " + content
        else:
            if buffer_content is not None:
                joined.append(f"{buffer_indent}//@ {buffer_content}")
                buffer_content = None
                buffer_indent = ""
            joined.append(line)

    if buffer_content is not None:
        joined.append(f"{buffer_indent}//@ {buffer_content}")

    return "\n".join(joined)

# Assumes that all JML annotations starts with "//@". Annotations in multi-line commments are not handled.
# Assumes that all JML annotations end within a single line. Splitting an annotation in multiple lines is not supported.
# This function processes one behavior at a time. A behavior is separated by the "also" keyword.
# Within a behavior, "requires" are classified as preconditions, and "assigns" and "ensures" as postconditions.
def extract_annotations(java_code: str) -> list[MethodSpecification]:
    lines = java_code.splitlines()
    jml_buffer = []
    methods = []
    method_signature = ""
    method_body = ""
    brace_count = 0
    is_fresh_return = False

    # Regex that Will Match a Java Method Declaration
    # https://stackoverflow.com/questions/68633/regex-that-will-match-a-java-method-declaration
    method_sig_pattern = re.compile(
        r'^(?:'
        r'(?:public|protected|private|static|final|synchronized|abstract|native|transient|volatile|strictfp|model)\s+'
        r'|@\w+(?:\s*\([^)]*\))?\s+'
        r'|/\*@.*?\*/\s*'
        r')*'
        r'[\w\<\>\[\],\s\.]+?\s+'   # return type
        r'([A-Za-z_]\w*)\s*'        # method name
        r'\([^\)]*\)\s*'            # arguments
        r'(?:throws\b[^{;]*)?\s*'   # optional throws
        r'(?:\{)?\s*$',             # may have { on this line or on the next; but no semicolon
        re.MULTILINE
    )

    for idx, line in enumerate(lines):
        stripped = line.strip()

        match = method_sig_pattern.search(stripped) # Will also match OpenJML model methods
        if not match:
            if stripped.startswith("//@"):
                jml_buffer.append(stripped)
                continue
        else:
            # Found a method signature
            full_signature = match.group(0)
            method_name, method_args_decl, method_return_type, method_signature = process_method_signature(full_signature)
            # Parse behaviors from jml_buffer
            behaviors = []
            current_pre = []
            current_post = []
            extra_qualifiers = []
            is_model = 'model' in stripped
            for annotation in jml_buffer:
                if "also" in annotation:
                    if current_pre or current_post:
                        behaviors.append(Behavior(current_pre, current_post))
                    current_pre = []
                    current_post = []
                elif "requires" in annotation:
                    current_pre.append(annotation)
                elif "assigns" in annotation or "ensures" in annotation or 'measured_by' in annotation:
                    current_post.append(annotation)
                    if "ensures" in annotation and "\\fresh(\\result)" in annotation:
                        is_fresh_return = True
                elif 'pure' in annotation or 'behaviors disjoint' in annotation or 'behaviors complete' in annotation:
                    extra_qualifiers.append(annotation)
            if current_pre or current_post:
                behaviors.append(Behavior(current_pre, current_post))
            jml_buffer = []

            # Collect method body (including invariants)
            method_body_lines = [line]
            brace_count = line.count("{") - line.count("}")
            i = idx + 1

            # If opening brace is not in the signature line, find it
            while brace_count == 0 and i < len(lines):
                method_body_lines.append(lines[i])
                brace_count += lines[i].count("{") - lines[i].count("}")
                i += 1

            # Now collect until braces are balanced
            while brace_count > 0 and i < len(lines):
                method_body_lines.append(lines[i])
                brace_count += lines[i].count("{") - lines[i].count("}")
                i += 1
            method_body = "\n".join(method_body_lines)

            methods.append(MethodSpecification(method_name, is_model, method_signature, method_args_decl, method_return_type, is_fresh_return, behaviors, extra_qualifiers, method_body))

    return methods

# This handles both baseline files from "SpecGenBench-Annotated" or the log results from "SpecGenBench-results"
# Some results have "multiple trials", where if it fails, it sends the error message to the LLM to re-generate.
# In this case, we want to get just the last, successfull trial.

# This also gets 'model method' from OpenJML 
# The tests are "wrapped" by a Java class.
# Traverse the file looking for the last Java class body.
def process_file(filepath: str) -> list[MethodSpecification]:
    with open(filepath) as f:
        code = f.read()
    code.expandtabs(tabsize=4) # replace tab with 4 spaces

    # Find all class declarations and their positions
    class_positions = []
    pattern = re.compile(r'^\s*(?:public\s+)?class\s+\w+\s*\{', re.MULTILINE)
    for match in pattern.finditer(code):
        class_positions.append(match.start())

    if not class_positions:
        print("file_processor.process_file(): error: class declaration code not found")
        return []

    # Get the last class declaration position
    start = class_positions[-1]

    # Find the matching closing brace for the class
    brace_count = 0
    in_class = False
    end = None
    for i, c in enumerate(code[start:], start=start):
        if c == '{':
            brace_count += 1
            in_class = True
        elif c == '}':
            brace_count -= 1
            if in_class and brace_count == 0:
                end = i + 1
                break

    if end is None:
        # If no matching closing brace, use the rest of the file
        class_code = code[start:]
    else:
        class_code = code[start:end]

    # preprocess source code:
    # make multiline comments /*@/ a single line //@
    # make comments that split specs into multiple lines in a single line
    # I'm not programming a JML parser, I need to have something easy to work with
    #print(f"Debug pre transform:\n{class_code}")
    class_code = preprocess_transform_source_code(class_code)
    #print(f"Debug post transform:\n{class_code}")

    return extract_annotations(class_code)


# Example usage:
if __name__ == "__main__":
    #specs = process_file("SpecGenBench-results/SpecGenBench/conversational/log-Absolute-2023_05_16_22_41_23.txt")

    parser = argparse.ArgumentParser(description="Process a Java source file, with OpenJML annotations in it.")
    parser.add_argument("source_file", help="Path to the Java source file")
    args = parser.parse_args()

    print(f"Processing file {args.source_file}")

    specs = process_file(filepath = args.source_file)

    print(f"Extracted {len(specs)} specs")

    for spec in specs:
        print(spec)
        print("Reconstructing behaviors preconditions:")
        print(spec.unify_preconditions())
        print("Reconstructing specification:")
        print(spec.reconstruct_spec())
        print("================BODY==================")
        print(spec.body)
        print()
        print("======================================")
