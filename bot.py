class Bot(object):
    def __init__(self):
        self.functions = {}
        
    def command(self,name):
        def decorator(function):
            def wrapper():
                return function
            self.functions[name] = function
            return wrapper()
        return decorator

    def execute(self,name,*args,**kwargs):
        return self.functions[name](*args,**kwargs)
