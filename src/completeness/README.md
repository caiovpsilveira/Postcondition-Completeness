The JML specifications and the .class (that the completeness check uses)
are provided in src/completeness/util

We want to *not* provide the .java source file, because it has already been verified.
Re-verifying adds +30s on each completeness_check call.
So we will provide only the .class and the .jml

Ref:
[OpenJML user guide](https://www.openjml.org/documentation/OpenJMLUserGuide.pdf).
Chapter 4.2 Finding files and classes: class, source, and specs paths

There are a number of common scenarios:
• Java source file on the command-line with a corresponding JML file on
the specifications path: the JML file is used as the specification of the
Java class, with any JML content in the Java source file completely ignored.
• Java source file on the command-line with no corresponding JML file on
the specifications path: the Java source file is used as its own JML specifi-
cation; if it contains no JML content, then default specifications are used.
• Java class file on the classpath or in the Java system library (referred to by
files on the command-line) and a corresponding JML file on the specifica-
tions path: the JML file is used as the specifications for the class file. Any
corresponding source file on the sourcepath or command-line is ignored.
• Java class file on the classpath or in the Java system library (referred to
by files on the command-line), no corresponding Java source file on the
sourcepath or command-line, and no corresponding JML file on the spec-
ifications path: the class file is used with default specifications.
