"""
Do not write over 120 columns per a line.
This rule counts a tab as 4 columns. TODO adapt unit test and run unit test

== Violation ==

    int HEEEEEEEEEEEEEEEEEEELLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO = 1;
    <== Violation. Too long

== Good ==

    int K; <== OK. It's short.
"""
from nsiqcppstyle_rulehelper import  *
from nsiqcppstyle_reporter import *
from nsiqcppstyle_rulemanager import *

def RunRule(lexer, line, lineno) :
    if not Match("^\s*$", line) :
        line = line.replace("\t", "    ")
        if len(line) > 120 :
            nsiqcppstyle_reporter.Error(DummyToken(lexer.filename, line, lineno, 0), __name__, 'Lines should very rarely be longer than 120 characters')

ruleManager.AddLineRule(RunRule)



###########################################################################################
# Unit Test
###########################################################################################

from nsiqunittest.nsiqcppstyle_unittestbase import *
class testRule(nct):
    def setUpRule(self):
        ruleManager.AddLineRule(RunRule)
