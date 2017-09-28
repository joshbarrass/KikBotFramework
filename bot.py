from flask import Flask,request,Response
from kik import KikApi, Configuration
from kik.messages import messages_from_json, TextMessage, PictureMessage,\
     PresetAttributions, SuggestedResponseKeyboard, TextResponse,\
     LinkMessage, CustomAttribution, VideoMessage, StartChattingMessage,\
     StickerMessage, ScanDataMessage

app = Flask(__name__)

class Bot(object):
    def __init__(self,username,api_key):
        self.functions = {}
        self.help = {}
        self.kik = KikApi(username, api_key)

    def start(self,route="/incoming"):
        @app.route(route,methods=["POST","GET"])
        def main():
            print self
            if not kik.verify_signature(request.headers.get('X-Kik-Signature'), request.get_data()):
                return Response(status=403)

            messages = messages_from_json(request.json['messages'])
            print "--Received Messages",messages
            to_send = None
            for message in messages:
                split = message.body.split(" ")
                command = split[0]
                text_data = split[1:]

            return Response(status=200)

                
        
    def command(self,name,help_entry=None):
        def decorator(function):
            def wrapper():
                return function
            self.functions[name] = function
            if isinstance(help_entry,str):
                self.help[name] = help_entry
            return wrapper()
        return decorator

    def execute(self,name,*args,**kwargs):
        return self.functions[name](*args,**kwargs)

    def command_list(self):
        return "\n".join([key+" : "+val for key,val in self.help.iteritems()])
