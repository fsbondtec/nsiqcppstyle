"""
Enforce spacing rules in initializer lists with braces.

This rule ensures consistent spacing around braces in initializer lists.
- Space after opening brace: { .field=value
- Space before closing brace: .field=value }
- No space directly inside empty braces: {}

== Violation ==

    Point p = {.x=10, .y=20};      <== Violation. No space after {
    Point p = { .x=10, .y=20};     <== Violation. No space before }
    Point p = { };                 <== Violation. Space in empty braces

== Good ==

    Point p = { .x=10, .y=20 };    <== OK. Space after { and before }
    Config c = { .width=800 };     <== OK.
    Empty e = {};                  <== OK. No space in empty braces
"""

from nsiqunittest.nsiqcppstyle_unittestbase import *
from nsiqcppstyle_rulehelper import *
from nsiqcppstyle_reporter import *
from nsiqcppstyle_rulemanager import *


def RunRule(lexer, contextStack):
    t = lexer.GetCurToken()
    
    # Check for opening brace
    if t.type == "LBRACE":
        t_next = lexer.PeekNextToken()
        t_next_skip = lexer.PeekNextTokenSkipWhiteSpaceAndCommentAndPreprocess()
        
        # Check if this is an empty initializer list {}
        if t_next_skip is not None and t_next_skip.type == "RBRACE":
            # Empty braces should not have space
            if t_next is not None and t_next.type == "SPACE":
                nsiqcppstyle_reporter.Error(t, __name__,
                    "No space allowed in empty braces")
            return
        
        # Check if this could be an initializer list (contains . for designated initializers)
        # Look ahead to see if we have designated initializers
        is_initializer_list = False
        for i in range(1, 10):
            check_token = lexer.PeekNextTokenSkipWhiteSpaceAndCommentAndPreprocess(i)
            if check_token is None:
                break
            if check_token.type == "PERIOD":
                is_initializer_list = True
                break
            if check_token.type in ["SEMI", "RBRACE"]:
                break
        
        if is_initializer_list:
            # Opening brace should be followed by space
            if t_next is not None and t_next.type not in ["SPACE", "LINEFEED"]:
                nsiqcppstyle_reporter.Error(t, __name__,
                    "Space required after opening brace in initializer list")
    
    # Check for closing brace
    elif t.type == "RBRACE":
        t_prev = lexer.PeekPrevToken()
        t_prev_skip = lexer.PeekPrevTokenSkipWhiteSpaceAndCommentAndPreprocess()
        
        # Check if this is an empty initializer list {}
        if t_prev_skip is not None and t_prev_skip.type == "LBRACE":
            # Empty braces - already checked in LBRACE case
            return
        
        # Check if this could be an initializer list
        is_initializer_list = False
        for i in range(1, 10):
            check_token = lexer.PeekPrevTokenSkipWhiteSpaceAndCommentAndPreprocess(i)
            if check_token is None:
                break
            if check_token.type == "PERIOD":
                is_initializer_list = True
                break
            if check_token.type in ["SEMI", "LBRACE"]:
                break
        
        if is_initializer_list:
            # Closing brace should be preceded by space
            if t_prev is not None and t_prev.type not in ["SPACE", "LINEFEED"]:
                nsiqcppstyle_reporter.Error(t, __name__,
                    "Space required before closing brace in initializer list")


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
        self.Analyze("test/thisFile.cpp", """
Point p = { .x=10, .y=20 };
""")
        self.ExpectSuccess(__name__)

    def test2(self):
        self.Analyze("test/thisFile.cpp", """
Point p = {.x=10, .y=20 };
""")
        self.ExpectError(__name__)

    def test3(self):
        self.Analyze("test/thisFile.cpp", """
Point p = { .x=10, .y=20};
""")
        self.ExpectError(__name__)

    def test4(self):
        self.Analyze("test/thisFile.cpp", """
Point p = {.x=10, .y=20};
""")
        self.ExpectError(__name__)

    def test5(self):
        self.Analyze("test/thisFile.cpp", """
Config cfg = { .width=800, .height=600, .fullscreen=false };
""")
        self.ExpectSuccess(__name__)

    def test6(self):
        self.Analyze("test/thisFile.cpp", """
matcher->locate(templ, { .searchRect=cv::Rect(-133, -190, 1289, 1403), .angleDomain=10 });
""")
        self.ExpectSuccess(__name__)

    def test7(self):
        self.Analyze("test/thisFile.cpp", """
Empty e = {};
""")
        self.ExpectSuccess(__name__)

    def test8(self):
        self.Analyze("test/thisFile.cpp", """
Empty e = { };
""")
        self.ExpectError(__name__)

    def test9(self):
        self.Analyze("test/thisFile.cpp", """
int arr[] = {1, 2, 3};
""")
        self.ExpectSuccess(__name__)

    def test10(self):
        self.Analyze("test/thisFile.cpp", """
Settings s = { .name="test", .value=42 };
""")
        self.ExpectSuccess(__name__)
