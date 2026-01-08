# Checks the logical equivalence between the methods of two Java code with annotation
# Logical equivalence: the pre(S1) imply pre(S2), and pre(S2) imply pre(S1)
# AND
# under the space state restricted by the preconditions, the post(S1) imply post(S2), and post(S2) imply post(S1).
# We can assume either pre(S1) or pre(S2) for the postcondition check, and this will only be valid iff pre(S1) <==> pre(S2)

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

from file_processor import process_file, MethodSpecification, Behavior
from typing import Union
import subprocess
import argparse
import sys
import os
import re

# Since we want to change the name to like "add_source1" and "add_source2",
# to compare both in the template.
# We also need to rename the body of other methods to account for the new updated method name
# NOTE: this is very primitive and will not work on tests with name overloading
def replace_method_names(methods: list[MethodSpecification], suffix: str) -> None:
    for method in methods:
        old_name = method.name
        new_name = method.name + suffix
        method.name = new_name

        for replace in methods:
            replace.replace_method_calls(old_name, new_name)

# Assumes that there is a method with the same uniq_signature
# in both source 1 and source2 {S1, S2}.
# For every tuple {S1, S2}, fill the equivalence template check # NO Need to check model methods, as they are inteded for assist in a prove only
# Check 'template.java'
def generate_openjml_equivalence_test(classname, source1_methods: list[MethodSpecification], source2_methods: list[MethodSpecification]) -> Union[str, int]:
    # assumes that the tuples are already ordered.
    #assert len(source1_methods) == len(source2_methods)
    if len(source1_methods) != len(source2_methods):
        return NUM_METHOD_MISMATCH

    # Pre-validation:
    # check if both source files contains the same methods, with the same signatures, parameters, etc
    for s1, s2 in zip(source1_methods, source2_methods):
        #assert s1.uniq_signature == s2.uniq_signature # This is updated after 'replace_method_names'
        if s1.uniq_signature != s2.uniq_signature:
            return SIGNATURE_MISMATCH
        # since the signature is the same, the list of arguments must be the same
        if len(s1.args_decl.split(",")) != len(s2.args_decl.split(",")):
            return SIGNATURE_MISMATCH
        if s1.return_type != s2.return_type:
            return SIGNATURE_MISMATCH
        if s1.is_model != s2.is_model:
            return SIGNATURE_MISMATCH
        
        if s1.is_model or s2.is_model:
            return MODEL_METHODS_NOT_IMPLEMENTED

    outStr = ""
    outStr += "public class " + classname + " {\n"

    for idx, (s1, s2) in enumerate(zip(source1_methods, source2_methods)):
        # reconstruct s1
        outStr += s1.reconstruct_spec()
        outStr += s1.body

        outStr += "\n\n"
        # reconstruct s2
        outStr += s2.reconstruct_spec()
        outStr += s2.body

        outStr += "\n\n"

        # This checks if pre(S1) ==> pre(S2) AND post(S2) ==> post(S1)
        outStr += s1.reconstruct_spec()
        outStr += f"//@ model public static {s1.return_type} preS1_implies_preS2_and_postS2_implies_postS1_m{idx}(" + s1.args_decl + ") {\n"
        if s1.return_type != "void":
            outStr += "//@     return " + s2.name + "(" + s1.args_use() + ");\n"
        else:
            outStr += "//@     " + s2.name + "(" + s1.args_use() + ");\n"
        outStr += "//@ }\n"
        
        outStr += "\n"
        # This checks if pre(S2) ==> pre(S1) AND post(S1) ==> post(S2)
        outStr += s2.reconstruct_spec()
        outStr += f"//@ model public static {s2.return_type} preS2_implies_preS1_and_postS1_implies_postS2_m{idx}(" + s2.args_decl + ") {\n"
        if s2.return_type != "void":
            outStr += "//@     return " + s1.name + "(" + s2.args_use() + ");\n"
        else:
            outStr += "//@     " + s1.name + "(" + s2.args_use() + ");\n"
        outStr += "//@ }\n"

    outStr += "}\n"
    return outStr

def check_logical_equivalence(source_file1_filepath: str, source_file2_filepath: str, check_feas: bool, check_null: bool, check_arith: bool, to_file: str):
    file1_methods_specs = process_file(source_file1_filepath)
    file2_methods_specs = process_file(source_file2_filepath)

    replace_method_names(file1_methods_specs, "_source1")
    replace_method_names(file2_methods_specs, "_source2")

    # pass to_file to Java not complain about 'class should be declared in Class.java'
    file_classname = os.path.splitext(os.path.basename(to_file))[0]
    union = generate_openjml_equivalence_test(file_classname, file1_methods_specs, file2_methods_specs)
    if isinstance(union, int):
        # propagate error code
        print("Stdout:")
        print("Stderr: Pre-requisites not met in equivalence_test.py:", err_code_to_str(int(union)))
        print("Return Code:", int(union))
        return int(union)

    test = str(union)

    with open(f"{to_file}", "w", encoding="utf-8") as outfile:
        outfile.write(test)

    feas_switch = "--check-feasibility=all" if check_feas else "--check-feasibility=none" 
    null_switch = "--nullable-by-default" if check_null else "--nonnull-by-default"
    arith_switch = "" if check_arith else "--arithmetic-failure=quiet"
    result = subprocess.run(f"openjml --esc --esc-max-warnings 1 {feas_switch} {null_switch} {arith_switch} --timeout 600 --progress {to_file}",
                            shell=True, capture_output=True, text=True)

    print("Stdout:", result.stdout)
    print("Stderr:", result.stderr)
    print("Return Code:", result.returncode)
    return result.returncode

# Example usage:
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check logical equivalence between two Java files with annotations.")
    parser.add_argument("source_file1", help="Path to the first Java source file (or the log)")
    parser.add_argument("source_file2", help="Path to the second Java source file (or the log)")

    parser.add_argument("-no_check_feas", action="store_true", default=False, help="Disable feasibility check")
    parser.add_argument("-no_check_null", action="store_true", default=False, help="Enable --nonnull-by-default (will assume that references are always valid)")
    parser.add_argument("-no_check_arith", action="store_true", default=False, help="Disable arithmetic failure")

    parser.add_argument("--to_file", help="The filepath which will be created to run OpenJML on")

    args = parser.parse_args()

    path1 = args.source_file1
    path2 = args.source_file2
    check_feas = not args.no_check_feas
    check_null = not args.no_check_null
    check_arith = not args.no_check_arith
    to_file = args.to_file

    retcode = check_logical_equivalence(path1, path2, check_feas, check_null, check_arith, to_file)
    sys.exit(retcode)
