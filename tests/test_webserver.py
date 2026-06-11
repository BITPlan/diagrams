"""
Created on 2023-10-07

@author: wf
"""
from ngwidgets.webserver_test import WebserverTest
from starlette.responses import Response

from dgs.ngwebserver import DiagramsWebServer
from dgs.diagrams_cmd import DiagramsCmd


class TestWebserver(WebserverTest):
    """Test the online diagrams service webserver"""

    def setUp(self, debug=False, profile=True):
        super().setUp(DiagramsWebServer, DiagramsCmd, debug=debug, profile=profile)

    def checkResponse(self, path: str, status_code: int) -> Response:
        """
        check the response for the given path for the given status code

        Args:
            path(str): the path for the request
            status_code(int): the expected status code

        Returns:
            Response: the response received
        """
        response = self.client.get(path)
        self.assertEqual(status_code, response.status_code)
        return response

    def testExamples(self):
        """
        test the examples RESTFul access
        """
        expected_status_code = 200
        for example in [
            "circo",
            "dot",
            "fdp",
            "mscgen",
            "neato",
            "osage",
            "patchwork",
            "plantuml",
            "sfdp",
            "twopi",
        ]:
            response = self.checkResponse(f"/example/{example}", expected_status_code)
            text = response.text
            marker = f"{example} example"
            debug = self.debug
            if debug:
                print(text)
            self.assertTrue(marker in text, example)

    def testGenerators(self):
        """
        test the /check Generators RESTFul access
        """
        # return
        expected_status_code = 200
        for generator in ["graphviz", "plantuml", "mscgen"]:
            response = self.checkResponse(f"/check/{generator}", expected_status_code)
            html = response.text
            debug = True
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
                "types": "png",
            },
        )
        self.assertEqual(200, response.status_code)
        json_text = response.json()
        debug = self.debug
        if debug:
            print(json_text)
        expected_json = """{
  "diagrams": {
    "png": {
      "url": "http://testserver/png/0x338668b9.png"
    }
  }
}"""
        self.assertEqual(expected_json, json_text)
        pass
