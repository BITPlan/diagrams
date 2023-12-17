import json
import os.path
import re
import zlib
from os.path import expanduser
from pathlib import Path
from subprocess import PIPE, Popen
from sys import platform


class ConfigurationError(Exception):
    """Exception raised for errors in the configuration.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
        super().__init__(message)


class Example(object):
    """Example handling"""

    @classmethod
    def get_base_path(cls) -> str:
        """
        get the Example base path
        """
        scriptdir = os.path.dirname(os.path.abspath(__file__))
        # for compatibility reasons try two paths
        for path in ["../web/examples", "../diagrams_examples"]:
            base_path = f"{scriptdir}/{path}"
            if os.path.isdir(base_path):
                return base_path
        raise ConfigurationError("examples not found in ../web or ../diagrams_examples")

    @classmethod
    def get(cls, generator: str) -> str:
        """
        get the example source code for the given generator

        Returns:
            str: the source code for the given generator
        """
        base_path = cls.get_base_path()
        example = f"{base_path}/example.{generator}"
        if os.path.isfile(example):
            txt = Path(example).read_text()
        else:
            txt = "no example for %s found" % generator
        return txt


class Command(object):
    """a command to be run using the shell environment"""

    def __init__(self, cmd, versionOption="--version", timeout=5, debug=False):
        """construct me"""
        self.cmd = cmd
        self.timeout = timeout
        self.versionOption = versionOption
        self.cmdpath = None
        self.debug = debug

    def call(self, args):
        """call me with the given args"""
        return self.docall(self.cmdpath, self.cmd, args)

    def callalias(self, alias, args):
        """call me with the given args"""
        return self.docall(self.cmdpath, alias, args)

    def docall(self, cmdpath, cmd, args):
        """call with a specific path and command"""
        cmdline = "%s%s %s" % (cmdpath, cmd, str(args))
        if self.debug:
            print("calling %s" % cmdline)
        process = Popen(cmdline, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        try:
            stdout, stderr = process.communicate(timeout=self.timeout)
            if self.debug:
                if stdout is not None:
                    print("stdout: %s" % stdout.decode("utf-8"))
                if stderr is not None:
                    print("stderr: %s" % stderr.decode("utf-8"))
            return stdout, stderr
        except Exception:
            process.kill()
            process.wait()  # Ensure the process has terminated
            return None, None

    def check(self):
        """
        check
        """
        cmdpaths = []
        # do we know the cmdpath?
        if self.cmdpath is None:
            # no we need to try multiple options in a specific order
            # prio #1: $HOME/bin
            home = expanduser("~")
            cmdpaths.append(home + "/bin/")
            # prio #2: e.g. Macports
            if platform == "darwin":
                cmdpaths.append("/opt/local/bin/")
            # prio #3: default path / no path
            # no path - use default PATH
            cmdpaths.append("")
        else:
            # we know the valid path
            cmdpaths.append(self.cmdpath)
        for cmdpath in cmdpaths:
            stdout, stderr = self.docall(cmdpath, self.cmd, self.versionOption)
            stdoutTxt = None
            stderrTxt = None
            if stdout is not None:
                stdoutTxt = stdout.decode("utf-8")
            if stderr is not None:
                stderrTxt = stderr.decode("utf-8")
            if (
                not "not found" in stderrTxt
                and not "No such file or directory" in stderrTxt
            ):
                self.cmdpath = cmdpath
                return stdoutTxt, stderrTxt
        return None, None


class Generators(object):
    """
    wrapper for available generators
    """

    generatorDict = {}
    """ the available generators """

    @staticmethod
    def get(generator):
        if len(Generators.generatorDict) == 0:
            for gen in Generators.generators():
                Generators.generatorDict[gen.id] = gen
        gen = None
        if generator in Generators.generatorDict:
            gen = Generators.generatorDict[generator]
        return gen

    @staticmethod
    def generatorIdForAlias(alias):
        for gen in Generators.generators():
            if alias in gen.aliases:
                return gen.id
        return None

    @staticmethod
    def generators():
        scriptdir = os.path.dirname(os.path.abspath(__file__))
        for plantumlpath in [".", ".."]:
            plantumljar = scriptdir + "/" + plantumlpath + "/plantuml.jar"
            if os.path.isfile(plantumljar):
                break
        if plantumljar is None:
            raise Exception("plantuml.jar not found in %s or .. of it", scriptdir)
        gens = [
            Generator(
                "graphviz",
                "GraphViz",
                "dot",
                "-V",
                logo="https://graphviz.org/Resources/app.png",
                url="https://www.graphviz.org/",
                aliases=[
                    "dot",
                    "neato",
                    "twopi",
                    "circo",
                    "fdp",
                    "sfdp",
                    "patchwork",
                    "osage",
                ],
                outputTypes=[
                    "png",
                    "svg",
                    "dot",
                    "xdot",
                    "ps",
                    "pdf",
                    "fig",
                    "gif",
                    "jpg",
                    "json",
                    "imap",
                    "cmapx",
                ],
            ),
            Generator(
                "mscgen",
                "Mscgen",
                "mscgen",
                "",
                logo="http://www.mcternan.me.uk/mscgen/img/msc-sig.png",
                url="http://www.mcternan.me.uk/mscgen/",
                outputTypes=["png", "svg", "eps", "ismap"],
            ),
            Generator(
                "plantuml",
                "PlantUML",
                "java -Djava.awt.headless=true -jar " + plantumljar,
                "-version",
                aliases=["plantuml"],
                logo="https://useblocks.com/assets/img/posts/plantuml_logo.png",
                url="https://plantuml.com",
                download="http://sourceforge.net/projects/plantuml/files/plantuml.jar/download",
                outputTypes=[
                    "png",
                    "svg",
                    "eps",
                    "pdf",
                    "vdx",
                    "xmi",
                    "scxml",
                    "html",
                    "txt",
                    "utxt",
                    "latex",
                    "latex:nopreamble",
                ],
            ),
        ]
        return gens


class GenerateResult(object):
    """
    a single generate result
    """

    def __init__(self, crc32, outputType, path, stdout, stderr):
        """
        construct me
        Args:
            crc32(string): the hash code to use
            outputType(string): e.g. "png", "svg"
            path(string): the path to the output file
            stdout(string): the STDOUT result of the generate command
            stderr(string): the STDERR result of the generate command
        """
        self.crc32 = crc32
        self.outputType = outputType
        self.path = path
        self.stdout = stdout
        self.stderr = stderr

    def errMsg(self):
        """
        decode my stdout and stderr to an error message

        Returns:
            string: a message containing stdout concatenated with stderr in utf-8 format
        """
        msg = ""
        if self.stdout is not None:
            msg = msg + self.stdout.decode("utf-8")
        if self.stderr is not None:
            msg = msg + self.stderr.decode("utf-8")
        return msg

    def asHtml(self):
        """return me as HTML"""
        url = "/render/%s/%s" % (self.outputType, self.crc32)
        if self.outputType in ["gif", "jpg", "png", "svg"]:
            return "<img src='%s'>" % url
        elif self.outputType in ["pdf"]:
            return "<object data='%s' width='640' height='640'></object>" % url
        else:
            return "<a href='%s'>%s %s</a>" % (url, self.outputType, self.crc32)

    def isValid(self):
        """check if i am valid"""
        valid = os.path.isfile(self.path) and not self.errMsg()
        return valid

    def asJson(self, baseurl: str) -> str:
        """
        Generate a JSON representation of the result.

        This function generates a JSON representation of a diagram (or an error)
        to be used by the Mediawiki diagrams extension.

        Args:
            baseurl (str): The base URL where the generated diagram can be found.

        Returns:
            str: A JSON string containing either the URL to the generated diagram
            or an error message if diagram generation failed.
        """
        error_message = self.errMsg()  # Assuming `err_msg` is a method in your class

        # Removing trailing slash from baseurl if present
        baseurl = str(baseurl).rstrip("/")

        if error_message:
            # Using f-string and json.dumps for better readability and handling of special characters in error_message
            json_txt = f"""{{
                "error": "generating {self.outputType} failed",
                "message": {json.dumps(error_message)}
            }}"""
        else:
            # Using f-string for better readability
            json_txt = f"""{{
  "diagrams": {{
    "{self.outputType}": {{
      "url": "{baseurl}/{self.outputType}/{self.crc32}.{self.outputType}"
    }}
  }}
}}"""

        return json_txt


class Generator(object):
    """a diagram generator"""

    @staticmethod
    def getOutputDirectory():
        home = expanduser("~")
        outputDir = home + "/.diagrams/"
        if not os.path.isdir(outputDir):
            os.mkdir(outputDir)
        return outputDir

    def __init__(
        self,
        genid,
        name,
        cmd,
        versionOption,
        logo=None,
        url=None,
        download=None,
        aliases=None,
        outputTypes=None,
        debug=False,
    ):
        """construct me"""
        self.id = genid
        self.name = name
        self.cmd = cmd
        self.gencmd = None
        self.logo = logo
        self.url = url
        self.htmlInfo = None
        self.download = download
        self.versionOption = versionOption
        if aliases is None:
            self.aliases = [cmd]
        else:
            self.aliases = aliases
        self.outputTypes = outputTypes
        self.debug = debug
        pass

    def getHtmlInfo(self):
        """get info on this generator to be displayed via  HTML"""
        # cache the info since getVersion is a costly process
        if self.htmlInfo is None:
            version = self.getVersion()
            self.htmlInfo = "<a href='%s' title='%s:%s'><img src='%s'/></a>" % (
                self.url,
                self.name,
                version,
                self.logo,
            )
        return self.htmlInfo

    def check(self):
        """check my version"""
        self.gencmd = Command(self.cmd, self.versionOption, debug=self.debug)
        return self.gencmd.check()

    def getVersion(self):
        """
        get the version
        """
        stdOutText, stdErrText = self.check()
        if stdOutText is not None and stdErrText is not None:
            outputText = stdOutText + stdErrText
        else:
            outputText = (
                "Couldn't get version for %s - you  might want to check the installation"
                % self.cmd
            )
        found = re.search(r"version.*[,)]", outputText)
        if found:
            version = found.group()
        else:
            # actually an error message
            version = outputText
            # invalidate gencmd
            self.gencmd = None
        return version

    @staticmethod
    def getHash(txt):
        """
        get a hash value for the given text
        Args:
            txt
        Returns:
            the hash value
        """
        hashValue = zlib.crc32(txt.encode()) & 0xFFFFFFFF
        hashId = hex(hashValue)
        return hashId

    def wrap(self, txt):
        """wraot the given text"""
        if self.id == "plantuml":
            txt = "@startuml\n%s\n@enduml\n" % txt
        return txt

    def generate(
        self, alias: str, txt: str, outputType: str, useCached: bool = True
    ) -> GenerateResult:
        """
        Generates output based on the provided text and parameters.

        Args:
        alias (str): The alias to be used for generating the output.
        txt (str): The text to be processed for generating the output.
        outputType (str): The type of output to be generated (e.g., "png", "svg").
        useCached (bool): If True, returns cached results if available. Defaults to True.

        Returns:
        GenerateResult: An object containing details about the generation process and results.
        """
        txt = self.wrap(txt)
        hashId = Generator.getHash(txt)
        inputPath = f"{Generator.getOutputDirectory()}{hashId}.txt"

        stdout = stderr = None
        if not (os.path.isfile(inputPath) and useCached):
            with open(inputPath, "w") as text_file:
                text_file.write(txt)

        outputPath = f"{Generator.getOutputDirectory()}{hashId}.{outputType}"
        if os.path.isfile(outputPath) and useCached:
            if self.debug:
                print(f"cached {outputType} #{hashId} from {outputPath}")
        else:
            if self.debug:
                print(f"generating {outputType} #{hashId} to {outputPath}")
            if self.id == "graphviz":
                args = f"-T{outputType} {inputPath} -o {outputPath}"
            elif self.id == "mscgen":
                args = f"-T{outputType} -i {inputPath} -o {outputPath}"
            else:
                args = f"-t{outputType} {inputPath}"
                alias = self.cmd
            if self.gencmd is None:
                self.check()
            stdout, stderr = self.gencmd.callalias(alias, args)

        result = GenerateResult(hashId, outputType, outputPath, stdout, stderr)
        return result
