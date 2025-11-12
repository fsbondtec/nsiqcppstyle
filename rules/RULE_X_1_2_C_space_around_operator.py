"""
Provide the space before and after operators.
There are variation to provide spaces.
In the binary operator.
Spaces should be provided before and after the operator.
For Division /, Multiplication* and Modulo % no spaces need to be provided

In the unary operator, Spaces should be provided before or after the operator.
However, when it's used in the (AA++), [--BB], {--KK}. It's OK not to provide spaces.

In the some operators(",", ";"), the spaces should be provided after the operator.
except for(;;) is also possible


== Violation ==

    for (a;b;c)  <== Violation. It should be (a; b; c)
    Hello(a,b,c) <== Violation. It should be (a, b, c)
    int k = 2+3; <== Violation. It should be 2 + 3
    c+++c;       <== Violation. It should be c++ + c

== Good ==

    int k = (2 + 3); <== OK. It's ok not to provide spaces before and after [, (, {
    int k = -2;      <== OK. Minus can be used to indicate minus value.
                         Therefore This rule doesn't care about it.
    for (a; b; c) {} <== OK
    Hello(a, b, c);  <== OK
    tt[c++]          <== OK. This rule doesn't care about the unary operator is used in the [ ( [
"""

from nsiqunittest.nsiqcppstyle_unittestbase import *
from nsiqcppstyle_rulehelper import *
from nsiqcppstyle_reporter import *
from nsiqcppstyle_rulemanager import *

operator = (
    "PLUS",
    "DIVIDE",
    "MODULO",
    "OR",
    "LSHIFT",
    "LOR",
    "LAND",
    "LE",
    "GE",
    "EQ",
    'EQUALS',
    'TIMESEQUAL',
    'DIVEQUAL',
    'MODEQUAL',
    'PLUSEQUAL',
    'MINUSEQUAL',
    'LSHIFTEQUAL',
    'RSHIFTEQUAL',
    'ANDEQUAL',
    'XOREQUAL',
    'OREQUAL'

)

nextoperator = (
    "SEMI",
    "COMMA",
)

unaryoperator = (
    'PLUSPLUS', 'MINUSMINUS'
)


def is_in_brace_initializer(lexer):
    """Check if current token is within brace initializer like {...}"""
    # Look backwards to find if we're inside curly braces
    # but NOT inside nested parentheses
    brace_depth = 0
    paren_depth = 0
    
    for i in range(1, 30):
        token = lexer.PeekPrevTokenSkipWhiteSpaceAndCommentAndPreprocess(i)
        if token is None:
            break
        
        if token.type == "RPAREN":
            paren_depth += 1
        elif token.type == "LPAREN":
            if paren_depth > 0:
                paren_depth -= 1
            # If we hit an opening paren before finding our brace, 
            # we're inside parentheses, not directly in braces
            elif paren_depth == 0 and brace_depth == 0:
                return False
        elif token.type == "RBRACE":
            brace_depth += 1
        elif token.type == "LBRACE":
            if brace_depth == 0:
                # Only return true if we're not nested in parentheses
                if paren_depth == 0:
                    # Found opening brace, check what precedes it
                    # Initializers are preceded by =, (, [, ,, or another {
                    prev = lexer.PeekPrevTokenSkipWhiteSpaceAndCommentAndPreprocess(i+1)
                    if prev and prev.type in ["EQUALS", "LPAREN", "LBRACKET", "COMMA", "LBRACE"]:
                        return True
                    # Also check for return statements: return {...}
                    if prev and prev.type == "RETURN":
                        return True
                return False
            brace_depth -= 1
        elif token.type == "SEMI" and brace_depth == 0:
            # Reached statement boundary without finding opening brace
            break
    
    return False


def RunRule(lexer, contextStack):
    t = lexer.GetCurToken()
    
    # Skip specific operators inside brace initializers
    # Only ignore spacing rules for EQUALS and COMMA inside {...}
    # Other operators should still be checked
    if is_in_brace_initializer(lexer) and t.type in ["EQUALS", "COMMA"]:
        return

    if t.type in operator:
        t2 = lexer.PeekNextToken()
        t3 = lexer.PeekPrevToken()
        t4 = lexer.PeekPrevTokenSkipWhiteSpaceAndCommentAndPreprocess()

        # Check for rvalue references (Type&& param) and move constructors
        if t.type == "LAND" and t4 is not None:
            # Check if this could be an rvalue reference
            next_token = lexer.PeekNextTokenSkipWhiteSpaceAndCommentAndPreprocess()
            
            # Rvalue reference pattern: Type&& identifier (only in function parameters)
            if next_token is not None and next_token.type == "ID":
                # More strict check: must have proper rvalue reference spacing and context
                if (t2 is not None and t2.type == "SPACE" and 
                    t3 is not None and t3.type != "SPACE"):
                    # Check if we're in a function parameter list (not in if/while conditions)
                    paren_depth = 0
                    found_function_context = False
                    found_control_structure = False
                    
                    for i in range(1, 20):
                        check_token = lexer.PeekPrevTokenSkipWhiteSpaceAndCommentAndPreprocess(i)
                        if check_token is None:
                            break
                        
                        # Check for control structures that would indicate logical &&
                        if check_token.type in ["IF", "WHILE", "FOR"] and paren_depth == 0:
                            found_control_structure = True
                            break
                        
                        if check_token.type == "RPAREN":
                            paren_depth += 1
                        elif check_token.type == "LPAREN":
                            if paren_depth == 0:
                                # We found the opening paren - check what precedes it
                                prev_of_paren = lexer.PeekPrevTokenSkipWhiteSpaceAndCommentAndPreprocess(i+1)
                                if prev_of_paren and prev_of_paren.type not in ["IF", "WHILE", "FOR"]:
                                    found_function_context = True
                                break
                            paren_depth -= 1
                        elif check_token.type in ["SEMI", "LBRACE", "RBRACE"] and paren_depth == 0:
                            break
                    
                    if found_function_context and not found_control_structure:
                        return  # This is an rvalue reference parameter, allow it
            
            # Original move constructor logic for special cases
            t5 = lexer.PeekPrevTokenSkipWhiteSpaceAndCommentAndPreprocess(2)
            isMoveCons = False
            if t5 is not None and t5.type == "LPAREN":
                t6 = lexer.PeekPrevTokenSkipWhiteSpaceAndCommentAndPreprocess(3)
                if (t6 is not None and t6.type == "FUNCTION" and t4.value == t6.value):
                    isMoveCons = True
                t6 = lexer.PeekPrevTokenSkipWhiteSpaceAndCommentAndPreprocess(4)
                if (t6 is not None and t6.type == "FUNCTION" and t6.value == "operator"):
                    isMoveCons = True
            
            if t2 is not None and t3 is not None and isMoveCons:
                if t3.type in ["SPACE", "LINEFEED", "PREPROCESSORNEXT"]:
                    nsiqcppstyle_reporter.Error(t, __name__,
                              "No Space Before move operator in '%s'" % t.value)
                if t2.type not in ["SPACE", "LINEFEED", "PREPROCESSORNEXT"]:
                    nsiqcppstyle_reporter.Error(t, __name__,
                              "Provide spaces after move operator '%s'" % t.value)
                return

        # for lambda [=]
        if t.type == "EQUALS":
            t5 = lexer.PeekNextTokenSkipWhiteSpaceAndCommentAndPreprocess()
            if t3.type == "LBRACKET" and t2.type == "RBRACKET":
                return
            if (t2.type == "SPACE" or t3.type == "SPACE") and t4.type == "LBRACKET" and t5.type == "RBRACKET":
                nsiqcppstyle_reporter.Error(t, __name__, 
                          "Do not use space in lambda operator")
                return
            # for default parameters like parms={} - check if we're in function parameter context
            if t2.type == "LBRACE":
                # Look for context indicators that this is a function parameter
                prev_tokens = []
                for i in range(1, 10):  # look back up to 10 tokens
                    prev_token = lexer.PeekPrevTokenSkipWhiteSpaceAndCommentAndPreprocess(i)
                    if prev_token is None:
                        break
                    prev_tokens.append(prev_token.type)
                    if prev_token.type in ["LPAREN", "COMMA"]:
                        # We're likely in function parameters
                        return
                    if prev_token.type in ["SEMI", "LBRACE", "RBRACE"]:
                        # We're likely in a statement or block, not parameters
                        break

        if t2 is not None and t3 is not None and (
                t4 is None or t4.type != "FUNCTION"):

            # no space for following types
            if t.type == "DIVIDE" or t.type == "MODULO" or t.type == "PLUS":
                return

            if t.pp == True and t.type == "DIVIDE":
                return
            if t2.type not in ["SPACE", "LINEFEED", "PREPROCESSORNEXT"] or t3.type not in [
                    "SPACE", "LINEFEED"]:
                t3 = lexer.GetPrevTokenSkipWhiteSpaceAndComment()
                if t3 is not None and t3.type != "OPERATOR" and not Match(
                        r"^\w*#include", t.line):
                    nsiqcppstyle_reporter.Error(t, __name__,
                                                "Provide spaces b/w operator '%s'" % t.value)
    elif t.type in nextoperator:
        t2 = lexer.PeekNextToken()
        t3 = lexer.PeekPrevToken()
        if t2 is not None and t2.type not in [
                "SPACE", "LINEFEED", "PREPROCESSORNEXT"] and not Match(r"^\w*#include", t.line):
            if t3 != None and (t2.type == "SEMI" or t3.type == "SEMI"):
                return #allow for(;;)
            nsiqcppstyle_reporter.Error(t, __name__,
                                        "Provide spaces after operator '%s'" % t.value)
    elif t.type in unaryoperator:
        t2 = lexer.PeekPrevToken()
        t3 = lexer.PeekNextToken()
        t4 = lexer.PeekPrevTokenSkipWhiteSpaceAndCommentAndPreprocess()
        if (Match(r"^\w*#include", t.line)):
            return
        if (t3 is not None and t3.type == "ID"):
            if t2.type not in ["COMMA", "OPERATOR", "SPACE", "LINEFEED", "LBRACE", "LPAREN", "LBRACKET"] and t3.type not in [
                    "SEMI", "SPACE", "LINEFEED", "RBRACE", "RPAREN", "RBRACKET"]:
                nsiqcppstyle_reporter.Error(t, __name__,
                                            "Provide spaces before operator '%s'" % t.value)

        if (t2 is not None and t2.type == "ID"):
            if t3.type not in ["COMMA", "OPERATOR", "SPACE", "LINEFEED", "RBRACE", "RPAREN", "RBRACKET"] and t3.type not in [
                    "SEMI", "SPACE", "LINEFEED", "RBRACE", "RPAREN", "RBRACKET"]:
                nsiqcppstyle_reporter.Error(t, __name__,
                                            "Provide spaces after operator '%s'" % t.value)


ruleManager.AddRule(RunRule)
ruleManager.AddPreprocessRule(RunRule)


##########################################################################
# Unit Test
##########################################################################


class testRule(nct):
    def setUpRule(self):
        ruleManager.AddRule(RunRule)
        ruleManager.AddPreprocessRule(RunRule)

    def test1(self):
        self.Analyze("test/thisFile.c",
                     """
int *a;
void operator=(EWE) {
HELLO = ewe << 3;
TEST <= 3;
TEST < 3;
TEST | C;
TEST & C;
A != 3;
t = a++;
}
""")
        self.ExpectSuccess(__name__)

    def test2(self):
        self.Analyze("test/thisFile.c",
                     """
(DD +ww);
""")
        self.ExpectError(__name__)

    def test3(self):
        self.Analyze("test/thisFile.c",
                     """
HELLO = ewe <<3;
""")
        self.ExpectError(__name__)

    def test4(self):
        self.Analyze("test/thisFile.c",
                     """
HELLo = TET ||B;
""")
        self.ExpectError(__name__)

    def test5(self):
        self.Analyze("test/thisFile.c", "#define KK(dsd) TET ||B;")
        self.ExpectError(__name__)

    def test6(self):
        self.Analyze("test/thisFile.c", "k = &b;")
        self.ExpectSuccess(__name__)

    def test7(self):
        self.Analyze("test/thisFile.c", "k=b;")
        self.ExpectError(__name__)

    def test8(self):
        self.Analyze("test/thisFile.c", "k|= b;")
        self.ExpectError(__name__)

    def test9(self):
        self.Analyze("test/thisFile.c", "k++c;")
        self.ExpectError(__name__)

    def test10(self):
        self.Analyze("test/thisFile.c", "#include <h/ds>")
        self.ExpectSuccess(__name__)

    def test11(self):
        self.Analyze("test/thisFile.c", "hash ^= hash << 4;")
        self.ExpectSuccess(__name__)

    def test12(self):
        self.Analyze("test/thisFile.c", """
#define KK() ewee;\\
hash ^= hash << 4;
""")
        self.ExpectSuccess(__name__)

    def test13(self):
        self.Analyze("test/thisFile.c", """
#define KK() ewee;\\
hash ^= hash<<4;
""")
        self.ExpectError(__name__)

    def test14(self):
        self.Analyze("test/thisFile.c", """
#include <magic++.h>
""")
        self.ExpectSuccess(__name__)

    def test15(self):
        self.Analyze("test/thisFile.c", """
m_mTabCommand.SetAt(nId++, p##TabName##TabCommand);
""")
        self.ExpectSuccess(__name__)

    def test16(self):
        self.Analyze("test/thisFile.c", """
m_mTabCommand.SetAt(++nId, p##TabName##TabCommand);
m_mTabCommand.SetAt(nId++dd);
""")
        self.ExpectError(__name__)

    def test17(self):
        self.Analyze("test/thisFile.c", """
string k = "k=b %s";
""")
        self.ExpectSuccess(__name__)

    def test18(self):
        self.Analyze("test/thisFile.c", """
sprintf(l_szConfigPath, ""
"print%log");
""")
        self.ExpectSuccess(__name__)

    def test19(self):
        self.Analyze("test/thisFile.c", r"""
sprintf(l_szConfigPath, "\\"
"print"
wewewe
wewe);
wewe
"ewewe"

""")
        self.ExpectSuccess(__name__)

    def test20(self):
        self.Analyze("test/thisFile.c", """
void create(const cv::Mat& templ, const cv::Mat& roiMask, const CreateParms& parms={});
""")
        self.ExpectSuccess(__name__)

    def test21(self):
        self.Analyze("test/thisFile.c", """
MyStruct s={field1, field2};
int arr[]={1, 2, 3};
""")
        self.ExpectError(__name__)

    def test22(self):
        self.Analyze("test/thisFile.cpp", """
class Contours {
public:
    Contours(std::vector<std::vector<cv::Point2f>>&& data);
};
""")
        self.ExpectSuccess(__name__)

    def test23(self):
        self.Analyze("test/thisFile.cpp", """
if (condition1&&condition2) {
}
""")
        self.ExpectError(__name__)

    def test24(self):
        self.Analyze("test/thisFile.cpp", """
class MyClass {
public:
    MyClass(MyClass&& other);  // Move constructor
    MyClass& operator=(MyClass&& other);  // Move assignment operator
};
""")
        self.ExpectSuccess(__name__)

    def test25(self):
        self.Analyze("test/thisFile.cpp", """
class MyClass {
public:
    MyClass(MyClass &&other);  // Move constructor with wrong spacing
};
""")
        self.ExpectError(__name__)

    def test26(self):
        self.Analyze("test/thisFile.cpp", """
class Foo {
public:
    Foo(Foo&& other) {}  // Move constructor - should be accepted per original code comment
};
""")
        self.ExpectSuccess(__name__)

    def test27(self):
        self.Analyze("test/thisFile.cpp", """
class Test {
public:
    Test& operator=(Test&& rhs) { return *this; }  // Move assignment
};
""")
        self.ExpectSuccess(__name__)

    def test28(self):
        self.Analyze("test/thisFile.cpp", """
void Foo(Foo&& other) {  // This should match original move constructor logic
}
""")
        self.ExpectSuccess(__name__)

    def test29(self):
        self.Analyze("test/thisFile.cpp", """
if (condition1 && condition2) {  // Logical AND - should need spaces
}
""")
        self.ExpectSuccess(__name__)

    def test30(self):
        self.Analyze("test/thisFile.cpp", """
if (condition1&&condition2) {  // Logical AND without spaces - should be error
}
""")
        self.ExpectError(__name__)

    def test31(self):
        self.Analyze("test/thisFile.cpp", """
MyStruct s1 = {field1, field2};
MyStruct s2 = { field1, field2 };
MyStruct s3 = {field1,field2};
MyStruct s4 = {field1, field2,field3 };
""")
        self.ExpectSuccess(__name__)

    def test32(self):
        self.Analyze("test/thisFile.cpp", """
int arr1[] = {1, 2, 3};
int arr2[] = { 1, 2, 3 };
int arr3[] = {1,2,3};
int arr4[] = {1, 2,3 };
""")
        self.ExpectSuccess(__name__)

    def test33(self):
        self.Analyze("test/thisFile.cpp", """
foo({x=1, y=2, z=3});
foo({ x=1, y=2, z=3 });
foo({x=1,y=2,z=3});
foo({x=1, y=2,z = 3 });
""")
        self.ExpectSuccess(__name__)

    def test34(self):
        self.Analyze("test/thisFile.cpp", """
foo(a, b, {x=1, y=2, z=3});
foo(a, b, { x=1, y=2, z=3 });
foo(a, b, {x=1,y=2,z=3});
foo(a, b, {x=1, y=2,z = 3 });
""")
        self.ExpectSuccess(__name__)

    def test35(self):
        self.Analyze("test/thisFile.cpp", """
foo(a, b, {x=1, y=2, z=3});
foo(a, b,{ x=1, y=2, z=3 });
foo(a,b, { x=1, y=2, z=3 });
""")
        self.ExpectError(__name__)

    def test36(self):
        self.Analyze("test/thisFile.cpp", """
cv::Point centers[] = {
    cv::Point(20, 10),
    cv::Point(40, 105)
};
""")
        self.ExpectSuccess(__name__)

    def test37(self):
        self.Analyze("test/thisFile.cpp", """
cv::Point centers[] = {
    cv::Point(20,10),
    cv::Point(40, 105)
};
""")
        self.ExpectError(__name__)

    def test38(self):
        self.Analyze("test/thisFile.cpp", """
cv::Point centers[] = {cv::Point(20,10), cv::Point(40, 105)};
""")
        self.ExpectError(__name__)
