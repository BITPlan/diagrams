'''
Created on 2023-10-07

@author: wf
'''
from tests.basetest import Basetest
from fastapi.testclient import TestClient
from dgs.ngwebserver import WebServer
from ngwidgets.cmd import WebserverCmd
import threading

class TestWebserver(Basetest):
    """ Test the online diagrams service webserver"""
    
    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        config=WebServer.get_config()
        # use a different port for testing then for production
        config.default_port+=10000
        cmd=WebserverCmd(config,WebServer)
        argv=[]
        args=cmd.cmd_parse(argv)
        self.ws = WebServer()
        self.ws_thread=threading.Thread(target=self.ws.run, name="webservice", kwargs={'args':args})
        self.ws_thread.start()
        self.client=TestClient(self.ws.app)
        
    def tearDown(self):
        """Shut down the webserver thread and perform cleanup."""
        # Check if the webserver thread is alive and try to shut it down
        if self.ws_thread.is_alive():
            # Logic to gracefully shut down the web server
            # (If possible, use an API call or set a flag that will stop the server)
            self.ws.stop()  # assuming there is a stop method in your WebServer class
            
            # Wait for the thread to finish
            self.ws_thread.join(timeout=2)  # provide a timeout to avoid hanging forever
            
            # If thread is still alive after timeout, terminate it forcefully (if possible)
            if self.ws_thread.is_alive():
                print("Warning: WebServer thread could not be stopped gracefully and was forcefully terminated.")
                # Potential forceful shutdown logic here, if possible
            
        # Additional cleanup logic here (if needed)
        self.client.close()  # clean up the TestClient
        
    def checkResponse(self,path:str,status_code:int)->'Response':
        """
        check the response for the given path for the given status code
        
        Args:
            path(str): the path for the request
            status_code(int): the expected status code
            
        Returns:
            Response: the response received
        """
        response = self.client.get(path)
        self.assertEqual(status_code,response.status_code)
        return response
        
    def testExamples(self):
        """
        test the examples RESTFul access
        """
        expected_status_code=200
        for example in ["circo","dot","fdp","mscgen","neato","osage","patchwork","plantuml","sfdp","twopi"]:
            response=self.checkResponse(f"/example/{example}", expected_status_code)
            text=response.text
            marker=f"{example} example"
            debug=self.debug
            if debug:
                print(text)
            self.assertTrue(marker in text,example)
            
    def testGenerators(self):
        """
        test the /check Generators RESTFul access
        """
        #return
        expected_status_code=200
        for generator in ["graphviz","plantuml","mscgen"]:
            response=self.checkResponse(f"/check/{generator}", expected_status_code)
            html=response.text
            debug=True
            if debug:
                print(html)
                
    def test_render_service(self):
        """
        test the diagrams render service
        """
        response = self.client.post(
        "/render/",
            headers={},
            json={
                "generator": "graphviz",
                "markup": "dot",
                "source": """digraph d {
a->b
}
""",
                "types": "png"
            },
        )
        self.assertEqual(200,response.status_code)
        json_text=response.json()
        debug=self.debug
        if debug:
            print (json_text)
        expected_json="""{
  "diagrams": {
    "png": {
      "url": "http://testserver/png/0x338668b9.png"
    }
  }
}"""
        self.assertEquals(expected_json,json_text)
        pass