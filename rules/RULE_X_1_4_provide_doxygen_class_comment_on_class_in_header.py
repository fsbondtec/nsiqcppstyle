"""
Provide the class doxygen comment.
It checks if there is doxygen sytle comment in front of each class definition on the header.

== Violation ==

= A.h = In A.cpp this is no problem
    class A { <== Violation. No doxygen comment.
    };
    
    /*        <== Violation. It's not a doxygen comment 
     *
     */
    class B { 
    };

== Good == 

= A.h =
    /**
     * blar blar
     */
    class A { <== OK
    };
    
    class B; <== Don't care. It's forward decl.
"""
from nsiqcppstyle_rulehelper import  *
from nsiqcppstyle_reporter import *
from nsiqcppstyle_rulemanager import *


def RunRule(lexer, currentType, fullName, decl, contextStack, typeContext) :
    ext = lexer.filename[lexer.filename.rfind("."):]
    if ext == ".h" :
        if not decl and currentType == "CLASS"  and typeContext != None:
            t = lexer.GetCurToken()
            lexer.PushTokenIndex()
            t2 = lexer.GetPrevTokenInType("COMMENT")
            lexer.PopTokenIndex()
            lexer.PushTokenIndex()
            t3 = lexer.GetPrevTokenInTypeList(["LBRACE", "SEMI", "PREPROCESSOR"], False, True)
            lexer.PopTokenIndex()
            if t2 != None and t2.additional == "DOXYGEN" : 
                if t3 == None or t2.lexpos > t3.lexpos :
                    return 
            nsiqcppstyle_reporter.Error(t, __name__, "Doxygen Comment should be provided in front of class def(%s) in header." % fullName)
ruleManager.AddTypeNameRule(RunRule)





###########################################################################################
# Unit Test
###########################################################################################

from nsiqunittest.nsiqcppstyle_unittestbase import *
class testRule(nct):
    def setUpRule(self):
        ruleManager.AddTypeNameRule(RunRule)   
