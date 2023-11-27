#
# This is used by LAC conversion projects to simulate the JavaScript endpoint
# Code is modified from original JavaScript and converted to Python
# Libraries are imported to support execution
import requests

class JavaScript:
    def __init__(self, javaScript: callable):
        self.calling = javaScript

    def execute(self, request: any):
        return self.calling(request)


class SysUtility:
    @staticmethod
    @classmethod
    def restPost(
        cls,
        post_url: str,
        some_str: str = "",
        header_settings: str = None,
        request_data: str = None,
    ):
        #resp = requests.post(post_url=post_url, headers=header_settings, data=request_data)
        pass

    @classmethod
    def restPut(
        cls,
        patch_url: str,
        some_str: str = "",
        header_settings: str = None,
        request_data: str = None,
    ):
        #resp = requests.patch(patch_url=patch_url, headers=header_settings, data=request_data)
        pass
    @staticmethod
    @classmethod
    def restGet(
        cls,
        get_url: str,
        some_str: str = "",
        header_settings: str = None,
        request_data: str = None,
    ):
        #resp = requests.get(get_url=get_url, headers=header_settings)
        pass
    
    @staticmethod
    @classmethod
    def findEntities(cls, entity_name: str, params: any):
        #get_url = {scheme}//{host}[:{port]}]/api/{entity_name} --params?
        #resp = requests.get(get_url=get_url)
        pass
