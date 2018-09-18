"""
Provide the space before and after operators.
TODO unit test
There are variation to provide spaces.
In the binary operator. 
Spaces should be provided before and after the operator.
For example, <, | ...
For Division /, * and % no spaces need to be provided

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

from nsiqcppstyle_rulehelper import  *
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
def RunRule(lexer, contextStack) :
    t = lexer.GetCurToken()
                
    #print(t)
    if t.type in operator :
        t2 = lexer.PeekNextToken()
        t3 = lexer.PeekPrevToken()
        t4 = lexer.PeekPrevTokenSkipWhiteSpaceAndCommentAndPreprocess();        
        t5 = lexer.PeekPrevTokenSkipWhiteSpaceAndCommentAndPreprocess(3);
        
        # move constructor --> accept form "Foo(Foo&& other)"
        if t.type == "LAND" and t4 != None and t5 != None and t4.value == t5.value:
            if t3.type in ["SPACE", "LINEFEED", "PREPROCESSORNEXT"]:
                nsiqcppstyle_reporter.Error(t, __name__,
                          "No Space Before move operator in '%s'" % t.value)
            if t2.type not in ["SPACE", "LINEFEED", "PREPROCESSORNEXT"]:
                nsiqcppstyle_reporter.Error(t, __name__,
                          "Provide spaces after move operator '%s'" % t.value)
            return
        
        if t2 != None and t3 != None  and (t4 == None or t4.type != "FUNCTION"):
            #if t.pp == True and t.type == "DIVIDE":
            # no space for following types
            if t.type == "DIVIDE" or t.type == "MODULO" or t.type == "PLUS":
                return
            if t2.type not in ["SPACE", "LINEFEED", "PREPROCESSORNEXT"] or t3.type not in ["SPACE", "LINEFEED"] :
                t3 = lexer.GetPrevTokenSkipWhiteSpaceAndComment()
                if t3 != None and t3.type != "OPERATOR" and not Match("^\w*#include", t.line):
                    nsiqcppstyle_reporter.Error(t, __name__, 
                          "Provide spaces b/w operator '%s'" % t.value)
    elif t.type in nextoperator :
        t2 = lexer.PeekNextToken()
        t3 = lexer.PeekPrevToken()
        if t2 != None and t2.type not in ["SPACE", "LINEFEED", "PREPROCESSORNEXT"] and not Match("^\w*#include", t.line):
            if t3 != None and (t2.type == "SEMI" or t3.type == "SEMI"):
                return #allow for(;;)
            nsiqcppstyle_reporter.Error(t, __name__, 
                          "Provide spaces after operator '%s'" % t.value)
    elif t.type in unaryoperator :
        t2 = lexer.PeekPrevToken()
        t3 = lexer.PeekNextToken()
        t4 = lexer.PeekPrevTokenSkipWhiteSpaceAndCommentAndPreprocess();
        if (Match("^\w*#include", t.line)) :
            return
        if (t3 != None and t3.type == "ID"):
            if t2.type not in ["COMMA", "OPERATOR", "SPACE", "LINEFEED", "LBRACE", "LPAREN", "LBRACKET"] and t3.type not in ["SEMI", "SPACE", "LINEFEED", "RBRACE", "RPAREN", "RBRACKET"]:
                nsiqcppstyle_reporter.Error(t, __name__, 
                          "Provide spaces before operator '%s'" % t.value)

        if (t2 != None and t2.type == "ID"):
            if t3.type not in ["COMMA", "OPERATOR", "SPACE", "LINEFEED", "RBRACE", "RPAREN", "RBRACKET"] and t3.type not in ["SEMI", "SPACE", "LINEFEED", "RBRACE", "RPAREN", "RBRACKET"]:
                nsiqcppstyle_reporter.Error(t, __name__, 
                          "Provide spaces after operator '%s'" % t.value)

ruleManager.AddRule(RunRule)
#ruleManager.AddPreprocessRule(RunRule)







###########################################################################################
# Unit Test
###########################################################################################

from nsiqunittest.nsiqcppstyle_unittestbase import *
class testRule(nct):
    def setUpRule(self):
        ruleManager.AddRule(RunRule)
        ruleManager.AddPreprocessRule(RunRule)
