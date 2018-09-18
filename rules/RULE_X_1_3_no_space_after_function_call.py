"""
No space after function call allowd.
foreach is an excpetion as it is used as a keyword in Qt, TODO unit test

== Violation ==

    myFunction (3,4); <== Violation. It should be myFunction(3,4);

== Good ==

	myFunction(3,4);
"""

from nsiqcppstyle_rulehelper import  *
from nsiqcppstyle_reporter import *
from nsiqcppstyle_rulemanager import *

def RunRule(lexer, contextStack):

    t = lexer.GetCurToken()
    if (t.type == 'ID' and t.value != "foreach" and t.value != "FOREACH"):
        t2 = lexer.PeekNextToken()
        t3 = lexer.PeekNextTokenSkipWhiteSpaceAndCommentAndPreprocess()
        if t3.type != None and t3.type == "LPAREN":
            if t2.type != None and t2.type == "SPACE" :
                nsiqcppstyle_reporter.Error(t, __name__, "no space after function call allowed '%s'" % t.value)

ruleManager.AddRule(RunRule)


###########################################################################################
# Unit Test
###########################################################################################
from nsiqunittest.nsiqcppstyle_unittestbase import *
class testRule(nct):
    def setUpRule(self):
        ruleManager.AddRule(RunRule)
                