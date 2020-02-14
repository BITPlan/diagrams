from subprocess import Popen,PIPE
from sys import platform
from os.path import expanduser
from pathlib import Path
import os.path
import sys
import re
from gremlin_python.process.graph_traversal import out

class Example(object):
    """ Example handling """
    @staticmethod
    def get(generator):
        scriptdir=os.path.dirname(os.path.abspath(__file__))
        example=scriptdir+"/../web/examples/example.%s" % generator
        if os.path.isfile(example):
            txt = Path(example).read_text()
        else:
            txt="no example for %s found" % generator
        return txt

class Command(object):
    """ a command to be run using the shell environment """
    def __init__(self,cmd,versionOption="--version",timeout=5,debug=False):
        """ construct me """
        self.cmd=cmd
        self.timeout=timeout
        self.versionOption=versionOption
        self.debug=debug

    def call(self,args):
        if self.debug:
            print ("calling %s" % str(args))
        process=Popen(args,shell=True,stdin=PIPE,stdout=PIPE,stderr=PIPE)
        try:
            stdout,stderr=process.communicate(timeout=self.timeout)
            if self.debug:
                if stdout is not None:
                    print ("stdout: %s" % stdout.decode('utf-8'))
                if stderr is not None:
                    print("stderr: %s" % stderr.decode('utf-8'))
            return stdout,stderr
        except Exception:
            process.kill()
            return None,None

    def check(self):
        cmdpaths=[""]
        home = expanduser("~")
        cmdpaths.append(home+"/bin/")
        if platform=="darwin":
            cmdpaths.append("/opt/local/bin/")
        for cmdpath in cmdpaths:
            cmdline="%s%s %s" % (cmdpath,self.cmd,self.versionOption)
            stdout,stderr=self.call(cmdline)
            stdoutTxt=None
            stderrTxt=None
            if stdout is not None:
                stdoutTxt=stdout.decode("utf-8")
            if stderr is not None:
                stderrTxt=stderr.decode("utf-8")
            if not "command not found" in stderrTxt and not "No such file or directory" in stderrTxt:
                return stdoutTxt,stderrTxt
        return None,None

class Generators(object):
    generatorDict={}
    """ the available generators """
    @staticmethod
    def get(generator):
        if len(Generators.generatorDict) is 0:
            for gen in Generators.generators():
                Generators.generatorDict[gen.id]=gen
        gen=None
        if generator in Generators.generatorDict:
            gen=Generators.generatorDict[generator]
        return gen        

    @staticmethod
    def generators():
        gens=[
            Generator("graphviz","GraphViz","dot","-V",logo="https://graphviz.gitlab.io/_pages/Resources/app.png",url="https://www.graphviz.org/",
                      aliases=[ 'dot', 'neato', 'twopi', 'circo', 'fdp', 'sfdp', 'patchwork', 'osage' ],
                      defaultType='png',
                      outputTypes=['dot', 'xdot', 'ps', 'pdf', 'svg', 'fig', 'png', 'gif', 'jpg', 'json', 'imap', 'cmapx']
                     ),
            Generator("mscgen","Mscgen","mscgen","",logo="http://www.mcternan.me.uk/mscgen/img/msc-sig.png", url="http://www.mcternan.me.uk/mscgen/",defaultType='png',outputTypes=['png', 'eps', 'svg', 'ismap']),
            Generator("plantuml","PlantUML","java -jar plantuml.jar","-version",aliases=['plantuml'],
                      logo="https://useblocks.com/assets/img/posts/plantuml_logo.png",
                      url="https://plantuml.com",
               defaultType='png',
               download="http://sourceforge.net/projects/plantuml/files/plantuml.jar/download",
               outputTypes=['png','svg','eps', 'pdf', 'vdx', 'xmi', 'scxml', 'html', 'txt', 'utxt',
			'latex', 'latex:nopreamble'])
        ]
        return gens

class Generator(object):
    """ a diagram generator """
    @staticmethod
    def getOutputDirectory():
        home = expanduser("~")
        outputDir=home+"/.diagrams/"
        if not os.path.isdir(outputDir):
            os.mkdir( outputDir);
        return outputDir

    def __init__(self,genid,name,cmd,versionOption,logo=None,url=None,download=None,defaultType=None,aliases=None,outputTypes=None, debug=False):
        """ construct me """
        self.id=genid
        self.name=name
        self.cmd=cmd
        self.logo=logo
        self.url=url
        self.htmlInfo=None
        self.download=download
        self.versionOption=versionOption;
        if aliases is None:
            self.aliases=[cmd]
        else:
            self.aliases=aliases
        self.defaultType=defaultType
        self.selectedType=defaultType
        self.outputTypes=outputTypes
        self.debug=debug
        pass
    
    def getHtmlInfo(self):
        if self.htmlInfo is None:
            version=self.getVersion()
            self.htmlInfo="<a href='%s' title='%s:%s'><img src='%s'/></a>" % (self.url,self.name,version,self.logo)
        return self.htmlInfo

    def check(self):
        """ check my version"""
        cmd=Command(self.cmd,self.versionOption,debug=self.debug)
        return cmd.check()
    
    def getVersion(self):    
        stdOutText,stdErrText=self.check()
        outputText=stdOutText+stdErrText
        found=re.search(r'version.*[,)]',outputText)
        if found:
            version=found.group()
        else:
            version=outputText    
        return version
    
    @staticmethod
    def getHash(txt):
        hashValue=hash(txt)
        # make it positive https://stackoverflow.com/a/18766856/1497139
        hashValue+=sys.maxsize+1
        hashId=hex(hashValue)
        return hashId
    
    def generate(self,txt,outputType):
        """ generate """
        hashId=Generator.getHash(txt)
        outputPath="%s%s.%s" % (Generator.getOutputDirectory(),hashId,outputType)
        if self.debug:
            print("generating %s #%s to %s" % (outputType,hashId,outputPath))
        args="%s -T %s -o  %s" % (self.cmd,outputType,outputPath)    
        cmd=Command(self.cmd,self.versionOption,debug=self.debug)    
        cmd.call(args)
        
