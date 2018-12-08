from typing import Union

from generators.python.common.InterfaceGenerator import InterfaceGenerator
from parser.classes import Interface, Attribute, Method

from common.file import file


class ServerGenerator(InterfaceGenerator):
    INTERFACE_NAME = 'interface'
    POST_ARG_NAME = 'data'

    def __init__(self):
        super().__init__('server_flask')
        self._assert_expr = None

    def generate(self, interface: Interface):
        self._add_files(InterfaceGenerator().generate(interface))
        self._add_file('flask_app.py',
                       file('static/app.py', __file__).read().splitlines())
        self._add_file('helpers.py',
                       file('static/helpers.py', __file__).read().splitlines())

        # Generate the REST API for that interface.
        self._set_current_file('app.py')
        self._add_line('from flask_app import app')
        self._add_line('import helpers')

        return super().generate(interface)

    def _path_line_decorator(self, methods: list):
        arguments = (self._str('/{path}'.format(path=self._get_path_string())),
                     'methods={methods}'.format(methods=self._str(methods)))

        return '@app.route({})'.format(', '.join(arguments))

    def _generate_function_body(self, obj: Union[Method, Attribute], arguments):
        if isinstance(obj, Attribute):
            methods = ['GET']
        else:
            methods = ['POST']

        with self._method_definition(obj.name,
                                     arguments,
                                     is_static=True,
                                     decorators=[self._path_line_decorator(methods)]):
            if isinstance(obj, Attribute):
                self._generate_attribute_body(obj)
            elif isinstance(obj, Method):
                self._generate_method_body(obj)
            else:
                raise NotImplementedError

    def _generate_attribute_body(self, attribute: Attribute):
        # evaluate the attribute
        self._assign('result', '{interface}.{path}()'
                     .format(interface=self.INTERFACE_NAME,
                             path='.'.join(self._get_path_list())))
        self._encapsulate_to_json('result', 'json_result')
        self._return_statement('json_result')

    @staticmethod
    def _method_arguments_to_names_list(arguments: list):
        return [argument.name for argument in arguments]

    def _generate_method_body(self, method: Method):
        function_obj = '{interface}.{path}'.format(interface=self.INTERFACE_NAME,
                                                   path='.'.join(self._get_path_list()))
        method_argument_names_list = self._method_arguments_to_names_list(method.arguments)

        self._function_call('helpers.run_method',
                            (str(method_argument_names_list),
                             function_obj),
                            'value')
        self._return_statement('value')
