FORMAT_ORIGINAL_GENERATION_PROMPT = """
Please generate JML specifications for the Java program given below.
```java
{src_code}
```
Note that:
+ You SHOULD generate `ensures` statements for every method, and `maintaining` statements for every loop.
+ Consider adding `/*@ spec_public @*/` specifications to all the members (especially private ones) within the class.
+ You SHOULD only insert the specifications into the source code given to you. You SHOULD NOT modify any content other than the comments inserted into the code.
+ You SHOULD output the code in its entirety, without omitting any original content.
"""

FORMAT_ORIGINAL_REFINEMENT_PROMPT = """
The following Java code is instrumented with JML specifications:
```java
{code}
```
Verifier failed to verify the specifications given above, with error information as follows:
```
{info}
```
Please refine the specifications, so that it can pass the verification.
Note that:
+ You SHOULD NOT modify any content other than the specifications inserted into the code.
+ You SHOULD output the code in its entirety, without omitting any original content.
"""


FORMAT_STRICT_GENERATION_PROMPT = """
Please generate JML specifications for the Java program given below.
```java
{src_code}
```
Rules (apply all, exactly as written):
- Add specifications only. DO NOT modify, delete, reorder, or rename existing Java code or its original comments.
- Every method must have at least one postcondition ('//@ ensures ...;' clause). Add more if needed to strengthen the specification.
- Every loop must have loop invariants ('//@ maintaining ...;' clauses).
- Do NOT use assumptions ('//@ assume ...;' clause). If some input or pre-state would trigger an exception (null dereference, OOB access, division by zero, negative sizes, etc.), exclude it with requires clauses.
- Do NOT specify exceptional behavior ('//@ signals ...;' clause). Exclude all exception-causing states via preconditions ('//@ requires ...;' clause).
- If the method returns a newly allocated object, use the following specification: '//@ ensures \\fresh(\\result);'.
- Provide a STRONG and COMPLETE specification: cover functional behavior, relationships among inputs, state effects, and return value. The specification must contain enough detail to reconstruct the original code unambiguously.
"""

FORMAT_STRICT_REFINEMENT_PROMPT = """
The following Java code is instrumented with JML specifications:
```java
{code}
```
Verifier failed to verify the specifications given above, with the following error information:
```
{info}
```
Please strengthen or correct the wrong specifications.
Rules (apply all, exactly as written):
- Add specifications only. DO NOT modify, delete, reorder, or rename existing Java code or its original comments.
- Every method must have at least one postcondition ('//@ ensures ...;' clause). Add more if needed to strengthen the specification.
- Every loop must have loop invariants ('//@ maintaining ...;' clauses).
- Do NOT use assumptions ('//@ assume ...;' clause). If some input or pre-state would trigger an exception (null dereference, OOB access, division by zero, negative sizes, etc.), exclude it with requires clauses.
- Do NOT specify exceptional behavior ('//@ signals ...;' clause). Exclude all exception-causing states via preconditions ('//@ requires ...;' clause).
- If the method returns a newly allocated object, use the following specification: '//@ ensures \\fresh(\\result);'.
- Provide a STRONG and COMPLETE specification: cover functional behavior, relationships among inputs, state effects, and return value. The specification must contain enough detail to reconstruct the original code unambiguously.
"""

WEAK_SPEC_ERR = """
The specification generated is valid, but incomplete (too weak).
Strengthen postconditions to capture all intended behavior.
Add explicit clauses for each semantic guarantee you intend:
- Existence / returned value characterization
- Minimality / first occurrence or uniqueness
- Bounds (index/value ranges, size relations)
- Ordering / sorting / monotonicity
- Preservation / permutation of elements
The specification must contain enough detail to reconstruct the original code unambiguously.
In other words, the specification must be equivalent to itself.
"""



FORMAT_REFINE_PROMPT = """
Your specification got the following error information:
```
{err_info}
```
Please generate again.
"""
