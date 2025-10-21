"""
All braces at top level (no indentation) should be located in separate line,
except for namespaces which can use either style.

== Violation ==

class A { <== ERROR (top level)
}

void function() { <== ERROR (top level)
}

== Good ==

namespace MyNamespace { <== OK (Exception for namespaces)
}

namespace MyNamespace  <== OK (Exception for namespaces)
{
}

namespace MyNamespace  <== OK (Exception for namespaces)
{
    class A { <== OK (indented, not top level)
    }
}

class A
{ <== CORRECT (top level)
    void method() { <== OK (indented, not top level)
    }
}

void function()
{ <== CORRECT (top level)
    if (condition) { <== OK (indented, not top level)
    }
}
"""
from nsiqunittest.nsiqcppstyle_unittestbase import *
from nsiqcppstyle_rulehelper import *
from nsiqcppstyle_reporter import *
from nsiqcppstyle_rulemanager import *


def RunRuleForFunction(lexer, fullName, decl, contextStack, typeContext):
    if not decl and typeContext is not None:
        t = lexer.GetNextTokenInType("LBRACE", False, True)
        if t is not None:
            t2 = typeContext.endToken
            if t2 is not None and t.lineno != t2.lineno:
                prevToken = lexer.GetPrevTokenSkipWhiteSpaceAndCommentAndPreprocess()  # noqa
                if prevToken is not None and prevToken.lineno == t.lineno:
                    # Check if declaration line starts at column 0 (top-level)
                    line = prevToken.line
                    lineIndent = len(line) - len(line.lstrip())
                    if lineIndent == 0:  # Top-level (no indentation)
                        nsiqcppstyle_reporter.Error(
                            t, __name__,
                            "The brace should be located in start of line")


def RunRuleForType(lexer, currentType, fullName, decl, contextStack,
                   typeContext):
    # Skip namespaces - they are allowed to have braces on same line
    if not decl and currentType != "NAMESPACE" and typeContext is not None:
        t = lexer.GetNextTokenInType("LBRACE", False, True)
        if t is not None:
            t2 = typeContext.endToken
            if t2 is not None and t.lineno != t2.lineno:
                prevToken = lexer.GetPrevTokenSkipWhiteSpaceAndCommentAndPreprocess()  # noqa
                if prevToken is not None and prevToken.lineno == t.lineno:
                    # Check if declaration line starts at column 0
                    line = prevToken.line
                    lineIndent = len(line) - len(line.lstrip())
                    if lineIndent == 0:  # Top-level (no indentation)
                        nsiqcppstyle_reporter.Error(
                            t, __name__,
                            "The brace should be located in start of line")


ruleManager.AddFunctionNameRule(RunRuleForFunction)
ruleManager.AddTypeNameRule(RunRuleForType)

##########################################################################
# Unit Test
##########################################################################


class testRule(nct):
    def setUpRule(self):
        ruleManager.AddFunctionNameRule(RunRuleForFunction)
        ruleManager.AddTypeNameRule(RunRuleForType)

    def test1(self):
        self.Analyze("thisfile.c", """
void function() {
}
""")
        self.ExpectError(__name__)

    def test2(self):
        self.Analyze("thisfile.c", """
void function()
{
}
""")
        self.ExpectSuccess(__name__)

    def test3(self):
        self.Analyze("thisfile.c", """
class A {
}
""")
        self.ExpectError(__name__)

    def test4(self):
        self.Analyze("thisfile.c", """
class A
{
}
""")
        self.ExpectSuccess(__name__)

    def test5(self):
        self.Analyze("thisfile.c", """
namespace MyNamespace {
    class A
    {
    };
}
""")
        self.ExpectSuccess(__name__)

    def test6(self):
        self.Analyze("thisfile.c", """
namespace MyNamespace
{
    class A
    {
    };
}
""")
        self.ExpectSuccess(__name__)

    def test7(self):
        self.Analyze("thisfile.c", """
class TopLevel
{
    void method() { // OK - indented
        if (true) { // OK - indented
        }
    }

    class InnerClass { // OK - indented
    };
};
""")
        self.ExpectSuccess(__name__)

    def test8(self):
        self.Analyze("thisfile.c", """
void topLevelFunction()
{
    void localFunction() { // OK - indented
    }
}
""")
        self.ExpectSuccess(__name__)
