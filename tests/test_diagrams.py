'''
Created on 2020-02-13

@author: wf
'''
import os
from dgs.diagrams import Command,Generator,Generators,Example
from tests.basetest import Basetest

class TestDiagrams(Basetest):
    """ Test the online diagrams service"""

    def testCommands(self):
        """
        test some commands
        """
        cmds=[Command("pwd","",debug=True),Command("java","-version",debug=True),Command("dot","-V",debug=True),Command("mscgen","",debug=True)]
        for cmd in cmds:
            cmd.check()
        pass
    
    def testGetGenerator(self):
        generators=["graphviz","mscgen","plantuml"]
        for generator in generators:
            gen=Generators.get(generator)
            assert gen is not None
            info=gen.getHtmlInfo()
            if self.debug:
                print(info)
    
    def testGeneratorCheck(self):
        for gen in Generators.generators():
            gen.debug=self.debug
            gen.check()
            
    def testGeneratorVersion(self):
        for gen in Generators.generators():
            gen.debug=self.debug
            version=gen.getVersion()    
            if self.debug:
                print(version)    
                
    def testGeneratorForAlias(self):
        for gen in Generators.generators():
            gen.debug=self.debug
            for alias in gen.aliases:
                genid=Generators.generatorIdForAlias(alias)
                assert genid==gen.id
            
    def testExamples(self):
        for gen in Generators.generators():
            for alias in gen.aliases:
                txt=Example.get(alias)
                if self.debug:
                    print (txt)
                assert not "no example for" in txt            

    def testGenerators(self):
        """
        test all generators
        """
        if self.debug:
            print ("outputDirectory is: %s" % (Generator.getOutputDirectory()))
        for gen in Generators.generators():
            gen.debug=self.debug
            for alias in gen.aliases:
                txt=Example.get(alias)
                result=gen.generate(alias,txt,"png")
                valid =result.isValid()
                if not valid:
                    print(result.errMsg())
                assert valid
            
    def testGenerateResult(self):
        '''
        test provoked error
        '''
        genid=Generators.generatorIdForAlias("plantuml")
        gen=Generators.get(genid)
        # provoke an error
        result=gen.generate('unknownalias','garbage input',"png")    
        json=result.asJson('http://www.doe.com') 
        debug=self.debug
        #debug=True
        if debug:
            print(f"json:{json}")
        # there is an image version of the error
        assert os.path.isfile(result.path)
        # which needs to be remove to make the test reproducible
        os.remove(result.path)
        assert "error" in json
