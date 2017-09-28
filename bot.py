from flask import Flask,request,Response
from kik import KikApi, Configuration
from kik.messages import messages_from_json, TextMessage, PictureMessage,\
     PresetAttributions, SuggestedResponseKeyboard, TextResponse,\
     LinkMessage, CustomAttribution, VideoMessage, StartChattingMessage,\
     StickerMessage, ScanDataMessage

app = Flask(__name__)

class Bot(object):
    def __init__(self,username,api_key,webhook):
        self.functions = {}
        self.help = {}
        self.kik = KikApi(username, api_key)
        self.kik.set_configuration(Configuration(
            webhook=webhook
        ))

    def start(self,route="/incoming"):
        @app.route(route,methods=["POST","GET"])
        def main():
            if not self.kik.verify_signature(request.headers.get('X-Kik-Signature'), request.get_data()):
                return Response(status=403)

            messages = messages_from_json(request.json['messages'])
            print "--Received Messages",messages
            to_send = None
            for message in messages:
                if isinstance(message,TextMessage):
                    split = message.body.split(" ")
                    command = split[0]
                    text_data = " ".join(split[1:])
                    if self.functions.has_key(command):
                        r = self.functions[command](text_data)
                        for m in r:
                            if m.to == None:
                                m.to = message.from_user
                            if m.chat_id == None:
                                m.chat_id = message.chat_id
                    else:
                        r = [TextMessage(
                            to=message.from_user,
                            chat_id=message.chat_id,
                            body="Unknown command.")]
                    self.kik.send_messages(r)
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
