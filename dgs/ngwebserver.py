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
from typing import Any
from dgs.diagrams import Generators,Generator,Example
from fastapi.responses import PlainTextResponse, HTMLResponse,FileResponse

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
        self.generators=Generators.generators()
        self.generator_id="graphviz"
        self.markup_dict={}
        
        @app.get('/example/{generator:str}')
        def example(generator:str):
            return self.example(generator)
        
        @app.get('/check/{generator:str}')
        def check(generator:str):
            return self.check(generator)
        
        @app.get('/render/{output_type}/{crc32}')
        def render(output_type:str,crc32:str):
            return self.render(output_type,crc32)
        
    @classmethod
    def examples_path(cls)->str:
        # the root directory (default: examples)
        path = os.path.join(os.path.dirname(__file__), '../diagrams_examples')
        path = os.path.abspath(path)
        return path
    
    def example(self,generator:str):
        """ get the example source code for the given generator """
        txt=Example.get(generator)
        return PlainTextResponse(txt)
    
    def check(self,generator:str):
        """
        get the html explanation for the given generator
        """
        gen=Generators.get(generator)
        if gen is not None:
            html=gen.getHtmlInfo()
            return HTMLResponse(html)
        else:
            msg=f"{generator} is not a valid generator"
            return PlainTextResponse(msg, 404)
        
    def render(self, output_type: str, crc32: str) -> Any:
        """
        Render a file response based on output type and CRC32 checksum.
    
        Args:
            output_type (str): The desired output file type/extension (without a leading dot).
            crc32 (str): The CRC32 checksum used to determine the file's name.
            
        Returns:
            Any: A file response which allows for direct rendering, e.g., in wikis.
        
        Note:
            The `crc32` argument can optionally contain the file extension.
            If provided, the method will strip it before appending the intended output_type.
    
        Example:
            render("pdf", "checksum123.pdf")
            The method will strip the ".pdf" from "checksum123.pdf" and append the intended ".pdf".
        """
        # Allow extension ending for direct rendering, e.g., in wikis
        ext = "." + output_type
        
        # If crc32 ends with the intended file extension, remove the extension
        if crc32.endswith(ext):
            crc32 = crc32[:-len(ext)]
        
        # Fetch the output directory
        output_directory = Generator.getOutputDirectory()
        
        # Construct the file name and path
        file_name = f"{crc32}{ext}"
        file_path = f"{output_directory}/{file_name}"
        
        # Generate and return a file response
        response = FileResponse(file_path)
        
        return response
    
    def selectGenerator(self,generator_id:str):
        try:
            self.generator=Generators.get(generator_id)
            html_info=self.generator.getHtmlInfo()
            self.gen_info.content=html_info
            self.markup_dict={}
            for alias in self.generator.aliases:
                self.markup_dict[alias]=alias
            self.markup_select.options=self.markup_dict
            self.markup_select.value=self.generator.aliases[0]
            self.markup_select.update()
        except Exception as ex:
            self.handle_exception(ex)
    
    def onGeneratorSelect(self,e):
        self.selectGenerator(e.value)
    
    async def home(self,_client:Client):
        '''
        provide the main content page
        
        '''
        self.setup_menu()
        gen_dict={}
        for gen in self.generators:
            gen_dict[gen.id]=gen.name
        with ui.row():
            self.generator_select=self.add_select("Generator:",gen_dict).bind_value(self, "generator_name")
            self.generator_select.change_handler=self.onGeneratorSelect
            self.markup_select=self.add_select("Markup:",self.markup_dict)
            self.gen_info=ui.html()
            self.generator_select.value=self.generator_id
        await self.setup_footer()

