# Checks the equivalence between two Java code with annotation

# Limitations:
# Only can handle trivial types: String, boolean, int, long, double, float, char and static arrays of these
# This assumes that both code will have 'exact' code (function names, arg names, arg order, etc), only changing the OpenJML specification
# For parameters passed by reference, this only works with Arrays for now.
#     * We need to clone each of these, and then after check if they are still equal

# TODO: accept 'int arr[]' aswell. Today only accepts 'int[] arr'

NUM_METHOD_MISMATCH = -1 # the files have a different number of methods provided
SIGNATURE_MISMATCH = -2 # the files have different methods

def err_code_to_str(ec):
    if ec == NUM_METHOD_MISMATCH:
        return "NUM_METHOD_MISMATCH"
    elif ec == SIGNATURE_MISMATCH:
        return "SIGNATURE_MISMATCH"
    else:
        return "UNKNOWN"

from file_processor import process_file, MethodSpecification, Behavior
from typing import Union
import subprocess
import argparse
import sys
import os

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

    for s1, s2 in zip(source1_methods, source2_methods):
        #assert s1.uniq_signature == s2.uniq_signature # This is updated after 'replace_method_names'
        if s1.uniq_signature != s2.uniq_signature:
            return SIGNATURE_MISMATCH
        # since the signature is the same, the list of arguments must be the same
        assert len(s1.args_decl.split(",")) == len(s2.args_decl.split(","))
        assert s1.return_type == s2.return_type
        assert s1.is_model == s2.is_model

    outStr = ""
    # Import some stuff that might be useful later
    outStr += "import java.util.Arrays;\n"
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


        # NOTE: model methods need to have equivalence checked?
        if s1.is_model:
            continue

        # Declare the equivalence function checks also as model methods

        # test if precondition of s1 ==> precondition of s2
        outStr += s1.unify_preconditions()
        outStr += f"//@ model public static void test_precond1_{idx}_implies(" + s1.args_decl + ") {\n"
        outStr += "//@     " + s2.name + "(" + s1.args_use() + ");\n"
        outStr += "//@ }\n"

        outStr += "\n"
        # test if precondition of s2 ==> precondition of s1
        outStr += s2.unify_preconditions()
        outStr += f"//@ model public static void test_precond2_{idx}_implies(" + s2.args_decl + ") {\n"
        outStr += "//@     " + s1.name + "(" + s2.args_use() + ");\n"
        outStr += "//@ }\n"

        outStr += "\n"
        # test if postconditions are equivalent
        # Some functions modify the input. Because we want to compare at the end, we need to clone the input
        # Currently only arrays are modifiable in place. So for each array in input, create a deep clone for s1 and for s2
        outStr += s1.unify_preconditions() # or s2, does not matter if they are equivalent. But the args names must match the precondition names
        outStr += f"//@ model public static void test_postcondition_{idx}_equivalence(" + s1.args_decl + ") {\n"

        # Replace arrays with deep clones
        s1_args_use = s1.args_use()
        s2_args_use = s2.args_use()

        arrays_by_ref_s1 = []
        arrays_by_ref_s2 = []

        # FIXME: this is WRONG if the function accepts more than 1 array as a parameter
        # It can be the case that the function expects the arrays to be the same reference!
        # Because it clones, it creates a deep copy
        # But we need to clone at least 1 array for each function tested, to be able to compare if they modify in the same way
        # Example: medium/IncrByOne.java should be something like this
        #//@ model public static void test_postcondition_0_equivalence(int[] a, int[] b) {
        #//@     int[] a_clone_0_s1 = a == null ? null : a.clone();
        #//@     int[] b_ref_1_s1 = b == null ? null : (b != a) ? b.clone() : a_clone_0_s1;
        #//@     int[] a_clone_0_s2 = a == null ? null : a.clone();
        #//@     int[] b_ref_1_s2 = b == null ? null : (b != a) ? b.clone() : a_clone_0_s2;
        #//@     incrByOne_source1(a_clone_0_s1,b_ref_1_s1);
        #//@     incrByOne_source2(a_clone_0_s2,b_ref_1_s2);
        #//@     assert Arrays.equals(a_clone_0_s1, a_clone_0_s2);
        #//@     assert Arrays.equals(b_ref_1_s1, b_ref_1_s2);
        #//@ }

        for idx, arg in enumerate(s1.args_decl.split(',')): # replace arrays with clones
            if '[]' in arg:
                arg_type = arg.strip().split(' ')[0]
                arg_name = arg.strip().split(' ')[1]
                clone_name_s1 = f'{arg_name}_clone_{idx}_s1'
                clone_name_s2 = f'{arg_name}_clone_{idx}_s2'
                arrays_by_ref_s1.append(clone_name_s1)
                arrays_by_ref_s2.append(clone_name_s2)

                s1_args_use = s1_args_use.replace(arg_name, clone_name_s1)
                s2_args_use = s2_args_use.replace(arg_name, clone_name_s2)

                # Avoid 'Infeasible' if the precondition already requires 'arr != null' in all behaviors
                # TODO: fix for when we have multiple 'arrays != null' in the same requires expr.
                # //@ requires x != null && y != null
                redundant_in_all_behaviors = True # Must be redundant in ALL behaviors
                for behavior in s1.behaviors:
                    redundant_in_this_behavior = False
                    for precond in behavior.preconditions:
                        for line in precond.splitlines():
                            line = ''.join([char for char in line if char != ' ' and char != '\t']) #remove spaces
                            if line == f'//@requires{arg_name}!=null;':
                                redundant_in_this_behavior = True
                                break
                        if not redundant_in_this_behavior:
                            redundant_in_all_behaviors = False
                            break

                if not redundant_in_all_behaviors:
                    # Otherwise the null from '? {arg_name}.clone() : null' is always unreachable
                    outStr += f'//@     {arg_type} {clone_name_s1} = {arg_name} != null ? {arg_name}.clone() : null;\n'
                    outStr += f'//@     {arg_type} {clone_name_s2} = {arg_name} != null ? {arg_name}.clone() : null;\n'
                else:
                    outStr += f'//@     {arg_type} {clone_name_s1} = {arg_name}.clone();\n'
                    outStr += f'//@     {arg_type} {clone_name_s2} = {arg_name}.clone();\n' 

        both_fresh_returns = s1.is_fresh_return and s2.is_fresh_return
        if both_fresh_returns:
            arrays_by_ref_s1.append("ret1")
            arrays_by_ref_s2.append("ret2")

        if s1.return_type != 'void':
            outStr += "//@     " + s1.return_type + " ret1 = " + s1.name + "(" + s1_args_use + ");\n"
            outStr += "//@     " + s2.return_type + " ret2 = " + s2.name + "(" + s2_args_use + ");\n"

            # Special case for comparing result types
            if '[]' in s1.return_type: # Arrays.
                if not both_fresh_returns: # Only compare non-fresh references.
                    outStr += "//@     assert Arrays.equals(ret1, ret2);\n"
            elif s1.return_type == 'String':
                outStr += "//@     assert ret1 != null && ret2 != null ? ret1.equals(ret2) : ret1 == ret2;\n"
            else: # Trivial data types
                outStr += "//@     assert ret1 == ret2;\n"
        else:
            outStr += "//@     " + s1.name + "(" + s1_args_use + ");\n"
            outStr += "//@     " + s2.name + "(" + s2_args_use + ");\n"

        # If it contained arrays, we also want to check if they are equal (if the function modifies by reference)
        assert len(arrays_by_ref_s1) == len(arrays_by_ref_s2)
        for i in range(len(arrays_by_ref_s1)):
            outStr += f"//@     assert Arrays.equals({arrays_by_ref_s1[i]}, {arrays_by_ref_s2[i]});\n"

        outStr += "//@ }\n"

    outStr += "}\n"
    return outStr

def check_equivalence(source_file1_filepath: str, source_file2_filepath: str, check_feas: bool, check_null: bool, check_arith: bool, to_file: str):
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
    # fails
    #test = check_equivalence("SpecGenBench/Abs/Abs.java", "SpecGenBench-results/SpecGenBench/conversational/log-Abs-2023_11_27_15_56_46.txt")
    # successes
    #test = check_equivalence("SpecGenBench-Annotated/Abs/Abs.java", "SpecGenBench-results/SpecGenBench/conversational/log-Abs-2023_11_27_16_28_50.txt")
    #test = check_equivalence("SpecGenBench-Annotated/AddLoopFor/AddLoopFor.java", "SpecGenBench-results/SpecGenBench/conversational/log-AddLoop-2023_07_09_18_02_39.txt")

    parser = argparse.ArgumentParser(description="Check equivalence between two Java files with annotations.")
    parser.add_argument("source_file1", help="Path to the first Java source file")
    parser.add_argument("source_file2", nargs="?", default=None, help="Path to the second Java source file (optional)." \
        "If not specified, will check equivalence of source_file1 <==> source_file1")

    parser.add_argument("-no_check_feas", action="store_true", default=False, help="Disable feasibility check")
    parser.add_argument("-no_check_null", action="store_true", default=False, help="Enable --nonnull-by-default (will assume that references are always valid)")
    parser.add_argument("-no_check_arith", action="store_true", default=False, help="Disable arithmetic failure")

    parser.add_argument("--to_file", help="The filepath which will be created to run OpenJML on")

    args = parser.parse_args()

    path1 = args.source_file1
    path2 = str(args.source_file2) if args.source_file2 is not None else path1
    check_feas = not args.no_check_feas
    check_null = not args.no_check_null
    check_arith = not args.no_check_arith
    to_file = args.to_file

    retcode = check_equivalence(path1, path2, check_feas, check_null, check_arith, to_file)
    sys.exit(retcode)
