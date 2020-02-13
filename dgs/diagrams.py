from subprocess import Popen,PIPE
from sys import platform
from os.path import expanduser
from pathlib import Path
import os.path

class Example(object):
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

    @staticmethod
    def generators():
        gens=[
            Generator("graphviz","GraphViz","dot","-V",url="https://www.graphviz.org/",
                      aliases=[ 'dot', 'neato', 'twopi', 'circo', 'fdp', 'sfdp', 'patchwork', 'osage' ],
                      defaultType='png',
                      outputTypes=['dot', 'xdot', 'ps', 'pdf', 'svg', 'fig', 'png', 'gif', 'jpg', 'json', 'imap', 'cmapx']
                     ),
            Generator("mscgen","Mscgen","mscgen","",url="http://www.mcternan.me.uk/mscgen/",defaultType='png',outputTypes=['png', 'eps', 'svg', 'ismap']),
            Generator("plantuml","PlantUML","java -jar plantuml.jar","-version",aliases=['plantuml'],url="https://plantuml.com",
               defaultType='png',
               download="http://sourceforge.net/projects/plantuml/files/plantuml.jar/download",
               outputTypes=['png','svg','eps', 'pdf', 'vdx', 'xmi', 'scxml', 'html', 'txt', 'utxt',
			'latex', 'latex:nopreamble'])
        ]
        return gens

class Generator(object):
    """ a diagram generator """

    def __init__(self,id,name,cmd,versionOption,url=None,download=None,defaultType=None,aliases=None,outputTypes=None, debug=False):
        """ construct me """
        self.id=id
        self.name=name
        self.cmd=cmd
        self.url=url
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

    def check(self):
        cmd=Command(self.cmd,self.versionOption,debug=self.debug)
        return cmd.check()
