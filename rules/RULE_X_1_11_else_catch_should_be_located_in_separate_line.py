"""
Keywords like else, catch should be located in separate line
after closing brace.

== Violation ==

    if (condition) {
        // code
    } else { <== Violation: else should be on separate line
        // code
    }

    try {
        // code
    } catch (Exception& e) { <== Violation: catch should be on separate line
        // code
    }

== Good ==

    if (condition) {
        // code
    }
    else { <== OK: else on separate line
        // code
    }

    try {
        // code
    }
    catch (Exception& e) { <== OK: catch on separate line
        // code
    }

"""
from nsiqunittest.nsiqcppstyle_unittestbase import *
from nsiqcppstyle_rulehelper import *
from nsiqcppstyle_reporter import *
from nsiqcppstyle_rulemanager import *


def RunRule(lexer, contextStack):
    t = lexer.GetCurToken()
    
    # Check for keywords that should be on separate lines
    keywords_to_check = ["ELSE", "CATCH"]
    
    if t.type in keywords_to_check:
        # Find the previous closing brace
        prevToken = lexer.GetPrevTokenSkipWhiteSpaceAndCommentAndPreprocess()
        
        if prevToken is not None and prevToken.type == "RBRACE":
            # Check if the keyword is on the same line as the closing brace
            if prevToken.lineno == t.lineno:
                nsiqcppstyle_reporter.Error(
                    t, __name__,
                    "Keyword '%s' should be located on a separate line "
                    "after closing brace" % t.value)


ruleManager.AddRule(RunRule)

##########################################################################
# Unit Test
##########################################################################


class testRule(nct):
    def setUpRule(self):
        ruleManager.AddRule(RunRule)

    def test1(self):
        self.Analyze("thisfile.cpp", """
void function() {
    if (condition) {
        doSomething();
    } else {
        doSomethingElse();
    }
}
""")
        self.ExpectError(__name__)

    def test2(self):
        self.Analyze("thisfile.cpp", """
void function() {
    try {
        riskyOperation();
    } catch (Exception& e) {
        handleError(e);
    }
}
""")
        self.ExpectError(__name__)

    def test3(self):
        self.Analyze("thisfile.cpp", """
void function() {
    if (condition) {
        doSomething();
    }
    else {
        doSomethingElse();
    }
}
""")
        self.ExpectSuccess(__name__)

    def test4(self):
        self.Analyze("thisfile.cpp", """
void function() {
    try {
        riskyOperation();
    }
    catch (Exception& e) {
        handleError(e);
    }
}
""")
        self.ExpectSuccess(__name__)

    def test5(self):
        self.Analyze("thisfile.cpp", """
void function() {
    if (condition) {
        doSomething();
    }
    else if (otherCondition) {
        doOtherThing();
    }
    else {
        doDefault();
    }
}
""")
        self.ExpectSuccess(__name__)

    def test6(self):
        self.Analyze("thisfile.cpp", """
void function() {
    try {
        riskyOperation();
    }
    catch (const std::exception& e) {
        handleStdException(e);
    }
    catch (...) {
        handleUnknownException();
    }
}
""")
        self.ExpectSuccess(__name__)
