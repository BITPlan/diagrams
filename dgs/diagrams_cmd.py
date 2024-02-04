"""
Created on 2023-10-06

@author: wf
"""
import sys
from argparse import ArgumentParser

from ngwidgets.cmd import WebserverCmd

from dgs.ngwebserver import DiagramsWebServer


class DiagramsCmd(WebserverCmd):
    """
    Command line for diagrams server
    """


def main(argv: list = None):
    """
    main call
    """
    cmd = DiagramsCmd(config=DiagramsWebServer.get_config(),webserver_cls=DiagramsWebServer)
    exit_code = cmd.cmd_main(argv)
    return exit_code


DEBUG = 0
if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-d")
    sys.exit(main())
