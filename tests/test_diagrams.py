'''
Created on 2020-02-13

@author: wf
'''
import unittest
from dgs.diagrams import Command,Generators,Example
debug=False
class Test(unittest.TestCase):


    def setUp(self):
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
            
    def testExamples(self):
        for gen in Generators.generators():
            for alias in gen.aliases:
                txt=Example.get(alias)
                if debug:
                    print (txt)
                assert not "no example for" in txt


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testDiagrams']
    unittest.main()