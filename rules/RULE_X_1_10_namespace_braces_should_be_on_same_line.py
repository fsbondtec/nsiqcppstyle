"""
Namespace braces should be located on the same line as the namespace declaration.
This applies to both top-level and nested namespaces.

== Violation ==

namespace MyNamespace
{ <== ERROR
    // content
}

namespace OuterNamespace {
    namespace InnerNamespace
    { <== ERROR (nested namespace)
        // content
    }
}

== Good ==

namespace MyNamespace { <== CORRECT
    // content
}

namespace MyNamespace::SubNamespace { <== CORRECT
    // content  
}

namespace OuterNamespace {
    namespace InnerNamespace { <== CORRECT (nested namespace)
        // content
    }
}
"""
from nsiqunittest.nsiqcppstyle_unittestbase import *
from nsiqcppstyle_rulehelper import *
from nsiqcppstyle_reporter import *
from nsiqcppstyle_rulemanager import *


def RunRuleForType(lexer, currentType, fullName, decl, contextStack,
                   typeContext):
    # Only check namespaces
    if not decl and currentType == "NAMESPACE" and typeContext is not None:
        t = lexer.GetNextTokenInType("LBRACE", False, True)
        if t is not None:
            t2 = typeContext.endToken
            if t2 is not None and t.lineno != t2.lineno:
                # Check if brace is NOT on same line as namespace declaration
                prevToken = lexer.GetPrevTokenSkipWhiteSpaceAndCommentAndPreprocess()  # noqa
                if prevToken is not None and prevToken.lineno != t.lineno:
                    # Apply rule to all namespaces (top-level and nested)
                    nsiqcppstyle_reporter.Error(
                        t, __name__,
                        "The namespace brace should be on same line")


ruleManager.AddTypeNameRule(RunRuleForType)

##########################################################################
# Unit Test
##########################################################################


class testRule(nct):
    def setUpRule(self):
        ruleManager.AddTypeNameRule(RunRuleForType)

    def test1(self):
        self.Analyze("thisfile.c", """
namespace MyNamespace
{
    class A {
    };
}
""")
        self.ExpectError(__name__)

    def test2(self):
        self.Analyze("thisfile.c", """
namespace MyNamespace {
    class A {
    };
}
""")
        self.ExpectSuccess(__name__)

    def test3(self):
        self.Analyze("thisfile.c", """
namespace A::B
{
    void func();
}
""")
        self.ExpectError(__name__)

    def test4(self):
        self.Analyze("thisfile.c", """
namespace A::B {
    void func();
}
""")
        self.ExpectSuccess(__name__)

    def test5(self):
        self.Analyze("thisfile.c", """
class TopLevel {
    namespace InnerNamespace
    {
        // This should now be checked (nested namespaces)
    }
};
""")
        self.ExpectError(__name__)

    def test6(self):
        self.Analyze("thisfile.c", """
namespace A { }
namespace B {
    namespace C
    {
        // This should now be checked (nested namespaces)
    }
}
""")
        self.ExpectError(__name__)

    def test7(self):
        self.Analyze("thisfile.c", """
class TopLevel {
    namespace InnerNamespace {
        // Correct: nested namespace with brace on same line
    }
};
""")
        self.ExpectSuccess(__name__)

    def test8(self):
        self.Analyze("thisfile.c", """
namespace A {
    namespace B {
        namespace C {
            // All correct: nested namespaces with braces on same line
        }
    }
}
""")
        self.ExpectSuccess(__name__)