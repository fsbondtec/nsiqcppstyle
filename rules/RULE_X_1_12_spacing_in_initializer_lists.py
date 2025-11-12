"""
Enforce spacing rules in initializer lists with braces.

This rule ensures consistent spacing around braces in initializer lists.
- No space after opening brace: {field1, field2}, {.field=value}, {1, 2, 3}
- No space before closing brace: {field1, field2}, {.field=value}, {1, 2, 3}
- Space after comma: , 
- No spaces around equals: .field=value (for designated initializers)
- No space directly inside empty braces: {}

== Violation ==

    MyStruct s = { field1, field2};    <== Violation. Space after {
    MyStruct s = {field1, field2 };    <== Violation. Space before }
    int arr[] = { 1, 2, 3 };           <== Violation. Spaces after { and before }
    Point p = { .x=10, .y=20};         <== Violation. Space after {
    Point p = {.x=10, .y=20 };         <== Violation. Space before }
    Point p = { };                     <== Violation. Space in empty braces
    Point p = {.x=10,.y=20};           <== Violation. No space after ,
    Point p = {.x = 10, .y = 20};      <== Violation. Spaces around =

== Good ==

    MyStruct s = {field1, field2};     <== OK. No space after { and before }
    int arr[] = {1, 2, 3};             <== OK. Arrays also follow this rule
    Point p = {.x=10, .y=20};          <== OK. No space after { and before }
    Config c = {.width=800};           <== OK.
    Empty e = {};                      <== OK. No space in empty braces
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
        
        # Check if this is an initializer list (either designated or regular)
        is_initializer_list = False
        
        # Check for designated initializer pattern: .field=value
        found_period = False
        found_id_after_period = False
        
        for i in range(1, 15):
            check_token = lexer.PeekNextTokenSkipWhiteSpaceAndCommentAndPreprocess(i)
            if check_token is None:
                break
            
            if check_token.type == "EQUALS" and found_id_after_period and found_period:
                is_initializer_list = True
                break
            
            if check_token.type == "ID" and found_period:
                found_id_after_period = True
            
            if check_token.type == "PERIOD":
                found_period = True
            
            if check_token.type in ["SEMI", "RBRACE"]:
                break
        
        # Also check for regular initializer list: Type var = {value1, value2}
        # Look backwards for EQUALS before LBRACE
        if not is_initializer_list:
            t_prev_skip = lexer.PeekPrevTokenSkipWhiteSpaceAndCommentAndPreprocess()
            if t_prev_skip is not None and t_prev_skip.type == "EQUALS":
                # Check if after = we have an ID (variable name) before
                for i in range(2, 10):
                    check_token = lexer.PeekPrevTokenSkipWhiteSpaceAndCommentAndPreprocess(i)
                    if check_token is None:
                        break
                    if check_token.type == "ID":
                        is_initializer_list = True
                        break
                    if check_token.type in ["SEMI", "LBRACE", "RBRACE"]:
                        break
        
        if is_initializer_list:
            # Opening brace should NOT be followed by space
            if t_next is not None and t_next.type == "SPACE":
                nsiqcppstyle_reporter.Error(t, __name__,
                    "No space allowed after opening brace in initializer list")
    
    # Check for closing brace
    elif t.type == "RBRACE":
        t_prev = lexer.PeekPrevToken()
        t_prev_skip = lexer.PeekPrevTokenSkipWhiteSpaceAndCommentAndPreprocess()
        
        # Check if this is an empty initializer list {}
        if t_prev_skip is not None and t_prev_skip.type == "LBRACE":
            # Empty braces - already checked in LBRACE case
            return
        
        # Check if this is an initializer list (designated or regular)
        is_initializer_list = False
        
        # First check for designated initializer pattern
        for i in range(1, 15):
            check_token = lexer.PeekPrevTokenSkipWhiteSpaceAndCommentAndPreprocess(i)
            if check_token is None:
                break
            
            # Look for EQUALS, then check if before that we have ID and PERIOD
            if check_token.type == "EQUALS":
                # Found equals, now check if before we have .field pattern
                for j in range(i + 1, i + 5):
                    prev_tok = lexer.PeekPrevTokenSkipWhiteSpaceAndCommentAndPreprocess(j)
                    if prev_tok is None:
                        break
                    if prev_tok.type == "PERIOD":
                        # Check if between PERIOD and EQUALS there is an ID
                        for k in range(i + 1, j):
                            mid_tok = lexer.PeekPrevTokenSkipWhiteSpaceAndCommentAndPreprocess(k)
                            if mid_tok is not None and mid_tok.type == "ID":
                                is_initializer_list = True
                                break
                        break
                if is_initializer_list:
                    break
            
            if check_token.type in ["SEMI", "LBRACE"]:
                # If we found LBRACE, might be a regular initializer list
                if check_token.type == "LBRACE":
                    # Check if before LBRACE there is EQUALS
                    for j in range(i + 1, i + 5):
                        prev_tok = lexer.PeekPrevTokenSkipWhiteSpaceAndCommentAndPreprocess(j)
                        if prev_tok is None:
                            break
                        if prev_tok.type == "EQUALS":
                            is_initializer_list = True
                            break
                        if prev_tok.type in ["SEMI", "LBRACE", "RBRACE"]:
                            break
                break
        
        if is_initializer_list:
            # Closing brace should NOT be preceded by space
            if t_prev is not None and t_prev.type == "SPACE":
                nsiqcppstyle_reporter.Error(t, __name__,
                    "No space allowed before closing brace in initializer list")
    
    # Check for comma in initializer lists
    elif t.type == "COMMA":
        t_prev = lexer.PeekPrevToken()
        
        # Check if we're in an initializer list
        is_initializer_list = False
        for i in range(1, 10):
            check_token = lexer.PeekPrevTokenSkipWhiteSpaceAndCommentAndPreprocess(i)
            if check_token is None:
                break
            if check_token.type == "PERIOD":
                is_initializer_list = True
                break
            if check_token.type in ["SEMI", "LBRACE"]:
                if check_token.type == "LBRACE":
                    is_initializer_list = True
                break
        
        if is_initializer_list:
            # Comma must be followed by space
            t_next = lexer.PeekNextToken()
            if t_next is not None and t_next.type not in ["SPACE", "LINEFEED"]:
                nsiqcppstyle_reporter.Error(t, __name__,
                    "Space required after comma in initializer list")
    
    # Check for equals sign in initializer lists
    elif t.type == "EQUALS":
        # Check if we're in a designated initializer list: {.field=value}
        # Pattern must be: LBRACE (optional: COMMA, other .field=value) PERIOD ID EQUALS
        # The PERIOD must come right before ID (no other ID between PERIOD and current ID)
        # This rules out: object.field = value (has ID before PERIOD)
        is_initializer_list = False
        t_prev_skip = lexer.PeekPrevTokenSkipWhiteSpaceAndCommentAndPreprocess()
        
        # Check if previous non-whitespace token is an identifier preceded by a period
        if t_prev_skip is not None and t_prev_skip.type == "ID":
            # Get the token before the ID (should be PERIOD for designated initializer)
            t_before_id = lexer.PeekPrevTokenSkipWhiteSpaceAndCommentAndPreprocess(2)
            
            if t_before_id is not None and t_before_id.type == "PERIOD":
                # Check what's before the PERIOD - should NOT be another ID
                # (that would be object.field, not .field)
                # Also NOT RBRACKET (that would be array[index].field)
                t_before_period = lexer.PeekPrevTokenSkipWhiteSpaceAndCommentAndPreprocess(3)
                
                if t_before_period is not None and t_before_period.type not in ["ID", "RBRACKET"]:
                    # Now verify we're inside braces
                    found_lbrace = False
                    
                    for i in range(3, 15):
                        check_token = lexer.PeekPrevTokenSkipWhiteSpaceAndCommentAndPreprocess(i)
                        if check_token is None:
                            break
                        if check_token.type == "LBRACE":
                            found_lbrace = True
                            break
                        if check_token.type == "SEMI":
                            # Found semicolon before LBRACE
                            break
                    
                    if found_lbrace:
                        is_initializer_list = True
        
        if is_initializer_list:
            # No spaces allowed around =
            t_prev = lexer.PeekPrevToken()
            t_next = lexer.PeekNextToken()
            
            if t_prev is not None and t_prev.type == "SPACE":
                nsiqcppstyle_reporter.Error(t, __name__,
                    "No space allowed before = in initializer list")
            
            if t_next is not None and t_next.type == "SPACE":
                nsiqcppstyle_reporter.Error(t, __name__,
                    "No space allowed after = in initializer list")


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
        """Test correct designated initializer formatting."""
        self.Analyze("test/thisFile.cpp", """
Point p = {.x=10, .y=20};
""")
        self.ExpectSuccess(__name__)

    def test1a(self):
        """Test space after opening brace is violation."""
        self.Analyze("test/thisFile.cpp", """
Point p = { .x=10, .y=20};
""")
        self.ExpectError(__name__)

    def test1b(self):
        """Test space before closing brace is violation."""
        self.Analyze("test/thisFile.cpp", """
Point p = {.x=10, .y=20 };
""")
        self.ExpectError(__name__)

    def test1c(self):
        """Test spaces after opening and before closing brace are violations."""
        self.Analyze("test/thisFile.cpp", """
Point p = { .x=10, .y=20 };
""")
        self.ExpectError(__name__)

    def test2(self):
        """Test multiple fields in designated initializer."""
        self.Analyze("test/thisFile.cpp", """
Config cfg = {.width=800, .height=600, .enabled=true};
""")
        self.ExpectSuccess(__name__)

    def test3(self):
        """Test designated initializer as function argument."""
        self.Analyze("test/thisFile.cpp", """
func(arg, {.field1=100, .field2=200});
""")
        self.ExpectSuccess(__name__)

    def test4(self):
        """Test empty braces without space."""
        self.Analyze("test/thisFile.cpp", """
Empty e = {};
""")
        self.ExpectSuccess(__name__)

    def test4a(self):
        """Test space in empty braces is violation."""
        self.Analyze("test/thisFile.cpp", """
Empty e = { };
""")
        self.ExpectError(__name__)

    def test5(self):
        """Test array initializer with correct spacing."""
        self.Analyze("test/thisFile.cpp", """
int arr[] = {1, 2, 3};
""")
        self.ExpectSuccess(__name__)

    def test5a(self):
        """Test space after opening brace in array initializer is violation."""
        self.Analyze("test/thisFile.cpp", """
int arr[] = { 1, 2, 3};
""")
        self.ExpectError(__name__)

    def test5b(self):
        """Test space before closing brace in array initializer is violation."""
        self.Analyze("test/thisFile.cpp", """
int arr[] = {1, 2, 3 };
""")
        self.ExpectError(__name__)

    def test6(self):
        """Test missing space after comma is violation."""
        self.Analyze("test/thisFile.cpp", """
Point p = {.x=10,.y=20};
""")
        self.ExpectError(__name__)

    def test7(self):
        """Test spaces around equals sign are violations."""
        self.Analyze("test/thisFile.cpp", """
Point p = {.x = 10, .y = 20};
""")
        self.ExpectError(__name__)

    def test7a(self):
        """Test space before or after equals sign is violation."""
        self.Analyze("test/thisFile.cpp", """
Point p = {.x= 10, .y =20};
""")
        self.ExpectError(__name__)

    def test8(self):
        """Test regular initializer without designated initializers."""
        self.Analyze("test/thisFile.cpp", """
Rect r {
    x, y,
    width, height
};
""")
        self.ExpectSuccess(__name__)

    def test8a(self):
        """Test multiline regular initializer with expressions."""
        self.Analyze("test/thisFile.cpp", """
Rect r {
    (int)(pos.x - size.w/2),
    (int)(pos.y - size.h/2),
    (int)size.w,
    (int)size.h,
};
""")
        self.ExpectSuccess(__name__)

    def test9(self):
        """Test member access assignment is not affected by rule."""
        self.Analyze("test/thisFile.cpp", """
for (int i = 0; i < n; i++) {
    obj.field = value;
}
""")
        self.ExpectSuccess(__name__)

    def test9a(self):
        """Test array element member access is not affected by rule."""
        self.Analyze("test/thisFile.cpp", """
for (int i = 0; i < n; i++) {
    array[i].x = value1;
    array[i].y = value2;
}
""")
        self.ExpectSuccess(__name__)

    def test10(self):
        """Test regular constructor initializer with correct spacing."""
        self.Analyze("test/thisFile.cpp", """
MyStruct s = {field1, field2, field3};
""")
        self.ExpectSuccess(__name__)

    def test10a(self):
        """Test space after opening brace in constructor initializer is violation."""
        self.Analyze("test/thisFile.cpp", """
MyStruct s = { field1, field2};
""")
        self.ExpectError(__name__)

    def test10b(self):
        """Test space before closing brace in constructor initializer is violation."""
        self.Analyze("test/thisFile.cpp", """
MyStruct s = {field1, field2 };
""")
        self.ExpectError(__name__)

    def test10c(self):
        """Test multiline constructor initializer with correct spacing."""
        self.Analyze("test/thisFile.cpp", """
MyStruct s = {
    field1,
    field2,
    field3
};
""")
        self.ExpectSuccess(__name__)
