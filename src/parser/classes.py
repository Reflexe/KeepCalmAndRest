class ClassName:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.namespaces = list(kwargs.get('namespaces', ()))


class Namespace:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.methods = list(kwargs.get('methods', ()))
        self.classes = list(kwargs.get('classes', ()))
        self.namespaces = list(kwargs.get('namespaces', ()))


class Method:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.return_value = kwargs.get('return_value')
        self.arguments = list(kwargs.get('arguments', ()))


class Class:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.methods = list(kwargs.get('methods', ()))
        self.attributes = list(kwargs.get('attributes', ()))


class Attribute:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.type = kwargs.get('type')


class Interface(Namespace):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, name='Interface')


class Argument:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.type = kwargs.get('type')
