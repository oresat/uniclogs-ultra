import log_interface
from api_resources import *
from loguru import logger
from flask import Flask
from flask_restful import Api



class Ultra:
    def __init__(self):
        self.logger = log_interface.init(__name__)
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.api.add_resource(HelloWorld, '/')

    def run(self):
        self.app.run(debug=True)

if __name__ == "__main__":
    Ultra().run()