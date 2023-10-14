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
from fastapi.responses import JSONResponse, PlainTextResponse, HTMLResponse,FileResponse
from pydantic import BaseModel
from fastapi import Request

class RenderOptions(BaseModel):
    generator: str
    source: str
    markup: str = "dot"
    types: str | None = None
    
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
        self.alias="dot"
        self.markup_dict={}
        self.output_type_dict={"png":"png"}
        self.output_type="png"
        
        @app.get('/example/{generator:str}')
        def example(generator:str):
            return self.example(generator)
        
        @app.get('/check/{generator:str}')
        def check(generator:str):
            return self.check(generator)
        
        @app.get('/render/{output_type}/{crc32}')
        def render(output_type:str,crc32:str):
            return self.render(output_type,crc32)
        
        @app.post('/render')
        async def render_service(render_options:RenderOptions,request: Request):
            return await self.render_service(render_options,request)
        
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
    
    async def render_service(self,render_options:RenderOptions,request:Request):
        """
        handle post request
        """
        gen=Generators.get(render_options.generator)
        target_format=render_options.types
        if target_format is None:
            target_format="png"
        result=gen.generate(render_options.markup,render_options.source,target_format)
        result_json=result.asJson(request.base_url)
        response=JSONResponse(content=result_json)
        return response
    
    def on_render(self,_e):
        """
        action when render button has been clicked
        """
        gen=self.generator
        alias=self.alias
        output_type=self.output_type
        source=self.source_area.value
        genResult=gen.generate(alias,source,output_type,useCached=True)
        if not genResult.isValid():
            msg=f"could not generate {output_type} for {gen.name} ({alias})"
            raise Exception(msg)
        html=genResult.asHtml()
        self.gen_result.content=html
        pass
        
    def on_example(self,_e):
        """
        action when example button has been clicked
        """
        try:
            example_txt=Example.get(self.alias)
            self.source_area.value=example_txt
        except Exception as ex:
            self.handle_exception(ex)
            
    def modify_select(self,select,options):
        """
        modify the given selection
        """
        select.value=None
        select.options=options
        select.update()
        first=list(options.keys())[0]
        select.value=first
        select.update()
        pass
    
    def selectGenerator(self,generator_id:str):
        """
        select the generator with the given generator_id
        
        Args:
            generator_id(str): the id of the generator to be selected
        """
        try:
            self.generator=Generators.get(generator_id)
            html_info=self.generator.getHtmlInfo()
            self.gen_info.content=html_info
            self.markup_dict={}
            for alias in self.generator.aliases:
                self.markup_dict[alias]=alias
            self.modify_select(self.markup_select,self.markup_dict)         
            self.output_type_dict={}
            for output_type in self.generator.outputTypes:
                self.output_type_dict[output_type]=output_type
            self.modify_select(self.output_type_select,self.output_type_dict)
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
        with ui.element("div").classes("w-full h-full"):
            with ui.splitter() as splitter:
                with splitter.before:
                    with ui.row():      
                        self.generator_select=self.add_select("Generator:",gen_dict).bind_value(self, "generator_name")
                        self.generator_select.change_handler=self.onGeneratorSelect
                        self.markup_select=self.add_select("Markup:",self.markup_dict).bind_value(self,"alias")
                        ui.button("example",on_click=self.on_example)
            
                    with ui.row():
                        self.output_type_select=self.add_select("output",self.output_type_dict).bind_value(self,"output_type")
                        ui.button("render",on_click=self.on_render)
                    with ui.row():
                        self.source_area=ui.textarea(placeholder="enter diagram markup here").props('clearable').props("cols=80").props("rows=25")
                with splitter.after:
                    with ui.row():
                        self.gen_info=ui.html()
                    with ui.row():
                        self.gen_result=ui.html()
        self.generator_select.value=self.generator_id
           
        await self.setup_footer()

