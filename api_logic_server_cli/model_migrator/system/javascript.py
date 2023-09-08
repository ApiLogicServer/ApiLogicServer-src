#
# This is used by LAC conversion projects to simulate the JavaScript endpoint
# Code is modified from original JavaScript and converted to Python 
# Libraries are imported to support execution

class JavaScript:
    
    def __init__(self, javaScript: function):
        
        self.calling = javaScript        

    
    def execute(self, request: any):
        return self.calling(request)