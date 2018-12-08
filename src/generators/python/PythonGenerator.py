from generators.Generator import Generator


class PythonGenerator(Generator):
    def __init__(self, module_name):
        super().__init__(module_name)
        self.current_indentation_level = 0

    def __indentation(self):
        return self.current_indentation_level * '    '

    class Indent:
        def __init__(self, generator):
            self.generator = generator

        def __enter__(self):
            self.generator.current_indentation_level += 1

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.generator.current_indentation_level -= 1

    def _indent(self):
        return self.Indent(self)

    def _add_line(self, content: str):
        return super()._add_line(self.__indentation() + content)

    def _function_definition(self, name, arguments=None):
        if arguments is None:
            arguments = ()

        self._add_line('def {name}({arguments}):'.format(name=name, arguments=', '.join(arguments)))
        return self._indent()

    def _method_definition(self, name, arguments=None, is_static: bool=None, decorators: list=None):
        if arguments is None:
            arguments = []

        if is_static is None:
            is_static = False

        if decorators is None:
            decorators = []

        if is_static:
            decorators.insert(0, '@staticmethod')
        else:
            arguments.insert(0, 'self')

        for decorator in decorators:
            self._add_line(decorator)

        return self._function_definition(name, arguments)

    def _class_definition(self, name: str, base: [str, None] = None):
        if base is not None:
            base = "({})".format(base)
        else:
            base = ''

        self._add_line('class {class_name}{base}:'.format(class_name=name,
                                                          base=base))

        return self._indent()

    def _assign(self, name, value):
        self._add_line('{name} = {value}'.format(name=name,
                                                 value=value))

    def _encapsulate_to_json(self, obj_name: str, result_name: str):
        return self._assign(result_name, 'json.dumps({obj_name})'.format(obj_name=obj_name))

    def _parse_json(self, obj_name: str, result_name: str):
        self._assign(result_name, 'json.loads({obj_name})'.format(obj_name=obj_name))

    def _return_statement(self, expression: str):
        self._add_line('return' + ' ' + expression)

    def _try_statement(self, try_code, except_code, except_types=None):
        self._add_line('try:')
        with self._indent():
            try_code()

        if not except_types:
            except_types = ''
        else:
            except_code = ','.join(except_types)

        self._add_line('except {}:'.format(except_types))
        with self._indent():
            except_code()

    def _assert_obj_is(self, obj, is_obj):
        self._add_line('assert isinstance({obj}, {is_obj})'.format(obj=obj, is_obj=is_obj))

    def _assert_equal(self, expr, expr2):
        self._add_line('assert ({expr}) == ({expr2})'.format(expr=expr, expr2=expr2))

    def _assert_not_equal(self, expr, expr2):
        self._add_line('assert ({expr}) != ({expr2})'.format(expr=expr, expr2=expr2))

    def _assert(self, expr):
        self._add_line('assert ({expr})'.format(expr=expr))

    def _function_call(self, expr, arguments=None, ret_variable=None):
        if arguments is None:
            arguments = ()

        if ret_variable is None:
            ret_variable = ''
        else:
            ret_variable = "{var} = ".format(var=ret_variable)

        self._add_line('{ret_variable}{expr}({arguments})'.format(expr=expr,
                                                                  arguments=', '.join(arguments),
                                                                  ret_variable=ret_variable))

    @staticmethod
    def _str(obj):
        return repr(obj)
