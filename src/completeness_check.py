# Checks if the methods in a Java source file (with JML annotations) have complete specifications

# Limitations:
# Only can handle trivial types: String, boolean, int, long, double, float, char, arrays of these and int[][].

# It uses a Library file with overloaded 'Equals' and 'DeepCopy'.
# The Equals method check if the *contents* are equally semantically.
# It disregards the references.
# Check src/completeness/util for the Library Specification in JML

NUM_METHOD_MISMATCH = -1 # the files have a different number of methods provided
SIGNATURE_MISMATCH = -2 # the files have different methods
MODEL_METHODS_NOT_IMPLEMENTED = -3 # It has OpenJML model ("ghost") methods
NO_ASSIGNS_LOCATIONS = -4 # no assigns or assignable. defaults to assign \everything

def err_code_to_str(ec):
    if ec == NUM_METHOD_MISMATCH:
        return "NUM_METHOD_MISMATCH"
    elif ec == SIGNATURE_MISMATCH:
        return "SIGNATURE_MISMATCH"
    elif ec == MODEL_METHODS_NOT_IMPLEMENTED:
        return "MODEL_METHODS_NOT_IMPLEMENTED"
    elif ec == NO_ASSIGNS_LOCATIONS:
        return "NO_ASSIGNS_LOCATIONS"
    else:
        return "UNKNOWN"

from file_processor import process_file, MethodSpecification
from typing import Union
import subprocess
import argparse
import sys
import os

def generate_openjml_completeness_test(classname, source_methods: list[MethodSpecification]) -> Union[str, int]:
    outStr = ""
    outStr += "import src.completeness.util.CompletenessUtil;\n"
    outStr += "public class " + classname + " {\n"

    def get_arg_type_from_name_map(args_decl: str) -> dict[str, str]:
        """Return mapping of arg name -> arg type from a MethodSpecification.args_decl string."""
        mapping: dict[str, str] = {}
        if not args_decl:
            return mapping
        for raw in args_decl.split(','):
            raw = raw.strip()
            if not raw:
                continue
            parts = raw.split()  # split on any whitespace
            if len(parts) < 2:
                continue
            arg_name = parts[-1]
            arg_type = " ".join(parts[:-1]).strip()
            if arg_type and arg_name:
                mapping[arg_name] = arg_type
        return mapping

    for idx, method in enumerate(source_methods):
        # NOTE: model methods need to be checked? lets ignore those for now.
        if method.is_model:
            return MODEL_METHODS_NOT_IMPLEMENTED

        # reconstruct the method
        outStr += method.reconstruct_spec()
        outStr += method.body

        outStr += "\n\n"

        outStr += method.unify_preconditions()
        outStr += f"//@ model public static void test_completeness_{idx}(" + method.args_decl + ") {\n"

        # Replace arrays with deep clones. S1 and S2 are two distinct calls with a independent start state
        args_by_ref_modified_s1 = [] # these will be checked at the end
        args_by_ref_modified_s2 = []
        s1_arg_names = method.args_use() # these have their names replaced with clones for the call
        s2_arg_names = method.args_use()

        modified_locations = set()
        if len(method.assigned_locations) == 0:
            return NO_ASSIGNS_LOCATIONS

        arg_types_by_name = get_arg_type_from_name_map(method.args_decl)

        for location in method.assigned_locations:
            if "\\nothing" in location: # skip assigns nothing
                continue
            elif "\\everything" in location: # we cannot handle everything
                return NO_ASSIGNS_LOCATIONS
            arg_name = location.split("[", 1)[0].strip() # We only want the name of the arg.
            modified_locations.add(arg_name)

        for idx, arg_name in enumerate(modified_locations): # replace references with deep clones
            # Currently only handle assigns locations that refer to parameters.
            arg_type = arg_types_by_name.get(arg_name)
            if not arg_type:
                assert 0
                continue

            # need to duplicate to have two independent calls over the same initial state: S1 and S2
            clone_name_s1 = f'{arg_name}_clone1'
            clone_name_s2 = f'{arg_name}_clone2'
            args_by_ref_modified_s1.append(clone_name_s1)
            args_by_ref_modified_s2.append(clone_name_s2)

            s1_arg_names = s1_arg_names.replace(arg_name, clone_name_s1)
            s2_arg_names = s2_arg_names.replace(arg_name, clone_name_s2)

            outStr += f'//@     {arg_type} {clone_name_s1} = CompletenessUtil.DeepCopy({arg_name});\n'
            outStr += f'//@     {arg_type} {clone_name_s2} = CompletenessUtil.DeepCopy({arg_name});\n' 

        # Completeness check on the return value
        if method.return_type != 'void':
            outStr += "//@     " + method.return_type + " ret1 = " + method.name + "(" + s1_arg_names + ");\n"
            outStr += "//@     " + method.return_type + " ret2 = " + method.name + "(" + s2_arg_names + ");\n"
            outStr += "//@     assert CompletenessUtil.Equals(ret1, ret2);\n"
        else:
            outStr += "//@     " + method.name + "(" + s1_arg_names + ");\n"
            outStr += "//@     " + method.name + "(" + s2_arg_names + ");\n"

        # If it assigns something (frame condition), we also want to check if the postconditions are complete for those locations
        assert len(args_by_ref_modified_s1) == len(args_by_ref_modified_s2)
        for i in range(len(args_by_ref_modified_s1)):
            outStr += f"//@     assert CompletenessUtil.Equals({args_by_ref_modified_s1[i]}, {args_by_ref_modified_s2[i]});\n"

        outStr += "//@ }\n"

    outStr += "}\n"
    return outStr

def check_completeness(source_file_filepath: str, check_null: bool, check_arith: bool, to_file: str):
    methods_specs = process_file(source_file_filepath)

    # pass to_file to Java not complain about 'class should be declared in Class.java'
    file_classname = os.path.splitext(os.path.basename(to_file))[0]
    union = generate_openjml_completeness_test(file_classname, methods_specs)
    if isinstance(union, int):
        # propagate error code
        print("Stdout:")
        print("Stderr: Pre-requisites not met in completeness_check.py:", err_code_to_str(int(union)))
        print("Return Code:", int(union))
        return int(union)

    test = str(union)

    with open(f"{to_file}", "w", encoding="utf-8") as outfile:
        outfile.write(test)

    null_switch = "--nullable-by-default" if check_null else "--nonnull-by-default"
    arith_switch = "--arithmetic-failure=hard" if check_arith else "--arithmetic-failure=quiet"

    cmd = [
        "openjml",
        "--esc",
        "--esc-max-warnings",
        "1",
        null_switch,
        arith_switch,
        "--timeout",
        "600",
        "--progress",
        to_file,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=700) # a bit more time than OpenJML timeout
    except subprocess.TimeoutExpired:
        print("Stdout:", "")
        print("Stderr:", "OpenJML exceeded external timeout")
        print("Return Code:", -1)
        return -1

    print("Stdout:", result.stdout)
    print("Stderr:", result.stderr)
    print("Return Code:", result.returncode)
    return result.returncode

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check if the methods in a Java file with JML annotations are complete.")
    parser.add_argument("source_file", help="Path to the Java source file with JML annotations")

    parser.add_argument("-no_check_null", action="store_true", default=False, help="Enable --nonnull-by-default (will assume that references are always valid)")
    parser.add_argument("-no_check_arith", action="store_true", default=False, help="Disable arithmetic failure")

    parser.add_argument("--to_file", help="The filepath which will be created to run OpenJML on", required=True)

    args = parser.parse_args()

    path1 = args.source_file
    check_null = not args.no_check_null
    check_arith = not args.no_check_arith
    to_file = args.to_file

    retcode = check_completeness(path1, check_null, check_arith, to_file)
    sys.exit(retcode)
