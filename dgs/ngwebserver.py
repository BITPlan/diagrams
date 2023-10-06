'''
Created on 2023-10-06

@author: wf
'''
from dgs.version import Version
from nicegui import app, ui, Client
from ngwidgets.input_webserver import InputWebserver
from ngwidgets.progress import NiceguiProgressbar
from ngwidgets.webserver import WebserverConfig
from ngwidgets.background import BackgroundTaskHandler
import os

class WebServer(InputWebserver):
    """
    WebServer class that manages the server 
    
    """
    @classmethod
    def get_config(cls)->WebserverConfig:
        copy_right="(c)2023 BITPlan GmbH"
        config=WebserverConfig(copy_right=copy_right,version=Version(),default_port=5003)
        return config
    
    def __init__(self):
        """Constructs all the necessary attributes for the WebServer object."""
        InputWebserver.__init__(self,config=WebServer.get_config())
        self.input_source=None
        self.output_path=None
        self.bth=BackgroundTaskHandler()
        app.on_shutdown(self.bth.cleanup())
        self.future=None
         
        @ui.page('/')
        async def home(client: Client):
            return await self.home(client)
        
        @ui.page('/settings')
        async def settings():
            return await self.settings()
        
    @classmethod
    def examples_path(cls)->str:
        # the root directory (default: examples)
        path = os.path.join(os.path.dirname(__file__), '../diagrams_examples')
        path = os.path.abspath(path)
        return path
    