"""
Created on 2023-10-07

@author: wf
"""

import json

from ngwidgets.webserver_test import WebserverTest
from starlette.responses import Response

from dgs.diagrams_cmd import DiagramsCmd
from dgs.ngwebserver import DiagramsWebServer


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
        # the answer is a json object, not a json string - see issue #23
        result = response.json()
        debug = self.debug
        if debug:
            print(json.dumps(result, indent=2))
        expected = {
            "diagrams": {"png": {"url": "http://testserver/render/png/0x338668b9.png"}}
        }
        self.assertEqual(expected, result)
        # the answered url must be served, see https://github.com/BITPlan/diagrams/issues/21
        url = result["diagrams"]["png"]["url"]
        image_response = self.client.get(url)
        self.assertEqual(200, image_response.status_code)
        self.assertEqual("image/png", image_response.headers["content-type"])
        self.assertTrue(image_response.content.startswith(b"\x89PNG"))

    def test_render_service_form(self):
        """
        test the render service with a form-encoded body as posted by the
        MediaWiki Diagrams extension, see https://github.com/BITPlan/diagrams/issues/22
        """
        response = self.client.post(
            "/render/",
            data={
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
        result = response.json()
        url = result["diagrams"]["png"]["url"]
        self.assertEqual("http://testserver/render/png/0x338668b9.png", url)

    def test_render_service_types_array(self):
        """
        test the render service with the PHP style types array of the
        MediaWiki Diagrams extension, see https://github.com/BITPlan/diagrams/issues/24
        """
        response = self.client.post(
            "/render/",
            data={
                "generator": "graphviz",
                "source": "digraph d { a->b }",
                "types[0]": "svg",
                "types[1]": "cmapx",
            },
        )
        self.assertEqual(200, response.status_code)
        result = response.json()
        self.assertIn("svg", result["diagrams"])
        self.assertTrue(result["diagrams"]["svg"]["url"].endswith(".svg"))
