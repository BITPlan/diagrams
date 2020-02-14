from subprocess import Popen,PIPE
from sys import platform
from os.path import expanduser
from pathlib import Path
import os.path
import sys
import zlib
import re

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
        self.cmdpath=None
        self.debug=debug
        
    def call(self,args):
        """ call me with the given args"""
        return self.docall(self.cmdpath,self.cmd,args)    
    
    def callalias(self,alias,args):
        """ call me with the given args"""
        return self.docall(self.cmdpath,alias,args)    

    def docall(self,cmdpath,cmd,args):
        """ call with a specific path and command"""
        cmdline="%s%s %s" % (cmdpath,cmd,str(args))
        if self.debug:
            print ("calling %s" % cmdline)
        process=Popen(cmdline,shell=True,stdin=PIPE,stdout=PIPE,stderr=PIPE)
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
        cmdpaths=[]
        # do we know the cmdpath?
        if self.cmdpath is None:
            # no we need to try multiple options in a specific order
            # prio #1: $HOME/bin
            home = expanduser("~")
            cmdpaths.append(home+"/bin/")
            # prio #2: e.g. Macports
            if platform=="darwin":
                cmdpaths.append("/opt/local/bin/")
            # prio #3: default path / no path
            # no path - use default PATH
            cmdpaths.append("")
        else:
            # we know the valid path
            cmdpaths.append(self.cmdpath)        
        for cmdpath in cmdpaths:
            stdout,stderr=self.docall(cmdpath,self.cmd,self.versionOption)
            stdoutTxt=None
            stderrTxt=None
            if stdout is not None:
                stdoutTxt=stdout.decode("utf-8")
            if stderr is not None:
                stderrTxt=stderr.decode("utf-8")
            if not "not found" in stderrTxt and not "No such file or directory" in stderrTxt:
                self.cmdpath=cmdpath
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
            Generator("plantuml","PlantUML","java -jar ../plantuml.jar","-version",aliases=['plantuml'],
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
        self.gencmd=None
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
        """ get info on this generator to be displayed via  HTML"""
        # cache the info since getVersion is a costly process
        if self.htmlInfo is None:
            version=self.getVersion()
            self.htmlInfo="<a href='%s' title='%s:%s'><img src='%s'/></a>" % (self.url,self.name,version,self.logo)
        return self.htmlInfo

    def check(self):
        """ check my version"""
        self.gencmd=Command(self.cmd,self.versionOption,debug=self.debug)
        return self.gencmd.check()

    def getVersion(self):
        stdOutText,stdErrText=self.check()
        outputText=stdOutText+stdErrText
        found=re.search(r'version.*[,)]',outputText)
        if found:
            version=found.group()
        else:
            # actually an error message
            version=outputText
            # invalidate gencmd
            self.gencmd=None
        return version

    @staticmethod
    def getHash(txt):
        hashValue=zlib.crc32(txt.encode()) & 0xffffffff
        hashId=hex(hashValue)
        return hashId

    def generate(self,alias,txt,outputType,useCached=True):
        """ generate """
        hashId=Generator.getHash(txt)
        inputPath="%s%s.%s" % (Generator.getOutputDirectory(),hashId,'txt')
        if not (os.path.isfile(inputPath) and  useCached):
            with open(inputPath, "w") as text_file:
                text_file.write("%s" % txt)
        outputPath="%s%s.%s" % (Generator.getOutputDirectory(),hashId,outputType)
        if os.path.isfile(outputPath) and useCached:
            if self.debug:
                print("cached %s #%s from %s"  % (outputType,hashId,outputPath))    
        else:         
            if self.debug:
                print("generating %s #%s to %s" % (outputType,hashId,outputPath))
            if self.id=="graphviz":
                args="-T%s %s -o  %s" % (outputType,inputPath,outputPath)
            elif self.id=="mscgen":
                args="-T%s -i %s -o  %s" % (outputType,inputPath,outputPath)    
            else:
                args="-t%s %s" % (outputType,inputPath)    
                alias=self.cmd    
            if self.gencmd is None:
                self.check()
            self.gencmd.callalias(alias,args)           
        return outputPath    
