from generators.python.common.InterfaceGenerator import InterfaceGenerator

from parser.classes import Interface


class ClientGenerator(InterfaceGenerator):
    def __init__(self, host, port, path=''):
        super().__init__('client-requests')

        self.port = str(port)
        self.host = host

    def generate(self, interface: Interface):
        self._set_current_file('main.py')
        self._add_line('import requests')

        return super().generate(interface)

    def _generate_function_body(self, obj, arguments: list):
        with self._method_definition(obj.name, arguments):

            self._assign('response', 'requests.post("{host}:{port}/{path}", json=kwargs)'
                         .format(host=self.host,
                                 port=self.port,
                                 path='/'.join(self._get_path_list()[1:])))

            self._return_statement('response.json()')
