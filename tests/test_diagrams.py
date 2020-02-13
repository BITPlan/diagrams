'''
Created on 13 Feb 2020

@author: wf
'''
import unittest
from dgs.diagrams import Command,Diagrams,Generators

class Test(unittest.TestCase):


    def setUp(self):
        self.diagrams=Diagrams()
        pass

    def tearDown(self):
        pass


    def testCommands(self):
        cmds=[Command("pwd","",debug=True),Command("java","-version",debug=True),Command("dot","-V",debug=True),Command("mscgen","",debug=True)]
        for cmd in cmds:
            cmd.check()
        pass
    
    def testGenerators(self):
        for gen in Generators.generators():
            gen.debug=True
            gen.check()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testDiagrams']
    unittest.main()