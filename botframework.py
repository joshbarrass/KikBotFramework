from flask import Flask,request,Response
from kik import KikApi, Configuration
from kik.messages import messages_from_json, TextMessage, PictureMessage,\
     PresetAttributions, SuggestedResponseKeyboard, TextResponse,\
     LinkMessage, CustomAttribution, VideoMessage, StartChattingMessage,\
     StickerMessage, ScanDataMessage, IsTypingMessage

app = Flask(__name__)

class Bot(object):
    def __init__(self,username,api_key,webhook,case_sensitive=False,command_list="Commands"):
        self.functions = {}
        self.help = {}
        self.keyboard_entries = []
        self.kik = KikApi(username, api_key)
        self.kik.set_configuration(Configuration(
            webhook=webhook
        ))
        self.case_sensitive = case_sensitive
        if not isinstance(command_list,str):
            command_list = None
        if not case_sensitive:
            if command_list != None:
                command_list = command_list.lower()
        self.command_list_command = command_list

    def start(self,route="/incoming"):
        @app.route(route,methods=["POST","GET"])
        def main():
            if not self.kik.verify_signature(request.headers.get('X-Kik-Signature'), request.get_data()):
                return Response(status=403)

            messages = messages_from_json(request.json['messages'])
            print "--Received Messages",messages
            to_send = None
            for message in messages:
                self.kik.send_messages([IsTypingMessage(
                    to=message.from_user,
                    chat_id=message.chat_id,
                    is_typing=True)])
                
                if isinstance(message,TextMessage):
                    split = message.body.split(" ")
                    command = split[0]
                    if not self.case_sensitive:
                        command = command.lower()
                    text_data = " ".join(split[1:])
                    if command == self.command_list_command:
                        r = [TextMessage(
                                to=message.from_user,
                                chat_id=message.chat_id,
                                body=self.command_list())]
                    elif self.functions.has_key(command):
                        r = self.functions[command](text_data)
                                    
                    else:
                        r = [TextMessage(
                            to=message.from_user,
                            chat_id=message.chat_id,
                            body="Unknown command.")]

                    for m in r:
                        if m.to == None:
                            m.to = message.from_user
                        if m.chat_id == None:
                            m.chat_id = message.chat_id
                        if m.keyboards == []:
                            keyboard = self.make_keyboard()
                            if len(keyboard.responses) > 0:
                                m.keyboards.append(keyboard)
                    
                    self.kik.send_messages(r)
            return Response(status=200)

    def make_keyboard(self):
        keyboard = SuggestedResponseKeyboard(
            hidden=False,
            responses=[TextResponse(x) for x in self.keyboard_entries])
        return keyboard
                
        
    def command(self,name,help_entry=None):
        if not self.case_sensitive:
            name = name.lower()
        def decorator(function):
            def wrapper():
                return function
            self.functions[name] = function
            if isinstance(help_entry,str):
                self.help[name] = help_entry
            return wrapper()
        return decorator

    def keyboard(self,entry):
        def decorator(function):
            def wrapper():
                return function
            self.keyboard_entries.append(entry)
            return wrapper()
        return decorator

    def execute(self,name,*args,**kwargs):
        return self.functions[name](*args,**kwargs)

    def command_list(self):
        return "\n".join([key+" : "+val for key,val in self.help.iteritems()])
