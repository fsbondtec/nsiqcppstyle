from nsiqunittest.nsiqcppstyle_unittestbase import *
from nsiqcppstyle_rulehelper import *
from nsiqcppstyle_reporter import *
from nsiqcppstyle_rulemanager import *


def RunRule(lexer, contextStack):
    # quickhack
    def PeekNextNextToken(lexer):
        lexer.PushTokenIndex()
        token = lexer._GetNextToken()
        token = lexer._GetNextToken()
        lexer.PopTokenIndex()
        return token

    t = lexer.GetCurToken()
    t2 = lexer.PeekNextToken()
    t3 = PeekNextNextToken(lexer)

    if t2 is None or t3 is None:
        return

    if t2.type == "SPACE" and t3.type == "LINEFEED":
        nsiqcppstyle_reporter.Error(t, __name__, "No Space at end of line")
        
    return


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
int a = 42;
""")
        self.ExpectSuccess(__name__)

    def test2(self):
        self.Analyze("test/thisFile.c", """
int a = 42; 
""")
        self.ExpectError(__name__)
