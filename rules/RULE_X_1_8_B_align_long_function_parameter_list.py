"""
align long function parameters on the first parameter when it's defined in multiple lines.


== Violation ==

    void functionA(int a, int b
              int c); <== Violation.

    void functionB(int a, int c,
                       int d) <== Violation

== Good ==

    void functionA(int a, int b
                   int c); <== OK.

"""
from nsiqunittest.nsiqcppstyle_unittestbase import *
from nsiqcppstyle_rulehelper import *
from nsiqcppstyle_reporter import *
from nsiqcppstyle_rulemanager import *
import nsiqcppstyle_state


def RunRule(lexer, fullName, decl, contextStack, context):
    lexer.GetNextTokenInType("LPAREN", False, True)
    rparen = lexer.GetNextMatchingToken(True)
    firstElement = lexer.PeekNextTokenSkipWhiteSpaceAndCommentAndPreprocess()
    firstElementLineNo = firstElement.lineno
    firstElementColumn = GetRealColumn(firstElement)

    tabsize = int(nsiqcppstyle_state._nsiqcppstyle_state.GetVar("tabsize", 4))

    while(True):
        t = lexer.GetNextTokenSkipWhiteSpaceAndCommentAndPreprocess()
        if t is None or t == rparen:
            break
        t2 = lexer.PeekPrevToken()
        if firstElementLineNo != t.lineno:
            if(GetIndentation(firstElement) == GetIndentation(t) - tabsize):
                break

            firstElementLineNo = t.lineno
            if firstElementColumn != GetRealColumn(t) and t2.value != '\t':
                nsiqcppstyle_reporter.Error(
                    t, __name__, "Incorrect align on long parameter list in front of '%s', it should be aligen in column %d." % (t.value, firstElementColumn))


ruleManager.AddFunctionNameRule(RunRule)

##########################################################################
# Unit Test
##########################################################################


class testRule(nct):
    def setUpRule(self):
        ruleManager.AddFunctionNameRule(RunRule)

    def test1(self):
        self.Analyze("test/thisFile.c",
                     """
void function(int k, int j
              int pp)
{
}
""")
        self.ExpectSuccess(__name__)

    def test2(self):
        self.Analyze("test/thisFile.c",
                     """
void function(int k, int j,
             int pp)
{
}
""")
        self.ExpectError(__name__)

    def test3(self):
        self.Analyze("test/thisFile.c",
                     """
void function(int k, int j,

             int pp)
{
}
""")
        self.ExpectError(__name__)

    def test4(self):
        self.Analyze("test/thisFile.c",
                     """
void function(int k, int j, int pp)
{
}
""")
        self.ExpectSuccess(__name__)

    def test5(self):
        self.Analyze("test/thisFile.c",
                     """
class A {
void function(int k, int j,
              int pp);
}
""")
        self.ExpectSuccess(__name__)

    def test6(self):
        self.Analyze("test/thisFile.c",
                     """
class A {
void function(int k, int j,
            int pp);
}
""")
        self.ExpectError(__name__)

    def test7(self):
        self.Analyze("test/thisFile.c",
                     """
class A {
void function(int k, int j,
              int pp)
{
    function(KK, DD,
             TT);
}
}
""")
        self.ExpectSuccess(__name__)

    def test8(self):
        self.Analyze("test/thisFile.c",
                     """
class A {
void function(int k, int j,
              int pp)
{
    function(KK, DD,
             TT);
}
}
""")
        self.ExpectSuccess(__name__)

    def test9(self):
        self.Analyze("test/thisFile.c",
                     """
Void aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa( int a,
                                          int b)
{
}
""")
        self.ExpectSuccess(__name__)

    def test10(self):
        self.Analyze("test/thisFile.c",
                     """
OrgDNSHandler::RESULT_CODE OrgDNSHandler::process( const NRootDNSConfig* pNRootDNSConfig,
                                                   const nano::Variant::List& params,
                                                   int a)
{
    return NULL;
};

void functionA(int a, int b
               int c);
""")
        self.ExpectSuccess(__name__)

    def test11(self):
        self.Analyze("test/thisFile.c",
                     """\tvoid function(int k, int j\n\t\tint pp)\n\t{\n}""")
        self.ExpectSuccess(__name__)

    def test12(self):
        self.Analyze("test/thisFile.c",
                     """\tvoid function(int k, int j\n\t\t\tint pp)\n\t{\n}""")
        self.ExpectError(__name__)
