from typing import Union

from generators.python.PythonGenerator import PythonGenerator
from parser.classes import Interface, Namespace, Class, Method, Attribute


class InterfaceGenerator(PythonGenerator):
    def __init__(self, module_name=''):
        super().__init__(module_name)
        self._set_current_file('common/interface.py')
        self.current_path = []

    class AddPath:
        def __init__(self, interface, fragment):
            self._interface = interface
            self._fragment = fragment

        def __enter__(self):
            self._interface.current_path.append(self._fragment)

        def __exit__(self, exc_type, exc_val, exc_tb):
            assert self._interface.current_path[-1] == self._fragment
            del self._interface.current_path[-1]

    def _add_path(self, fragment):
        return self.AddPath(self, fragment)

    def _generate_interface(self, namespace: Namespace):
        with self._class_definition(namespace.name):
            self._generate_namespace_initializer(namespace)
            self._generate_namespaces(namespace.namespaces)
            self._generate_methods(namespace.methods)
            self._generate_classes(namespace.classes)

    def generate(self, interface: Interface):
        self._generate_interface(interface)
        return self.files()

    def _generate_namespaces(self, namespaces: list):
        self._generate_namespaces_classes(namespaces)

    def _generate_namespaces_classes(self, namespaces: list):
        for namespace in namespaces:
            self._generate_namespace(namespace)

    def _generate_classes(self, classes: list):
        self._generate_classes_classes(classes)

    def _generate_classes_classes(self, classes):
        for klass in classes:
            self._generate_class(klass)

    @staticmethod
    def _class_name(klass: Class):
        return 'class_' + klass.name

    @staticmethod
    def _namespace_name(namespace: Namespace):
        return 'namespace_' + namespace.name

    @staticmethod
    def _obj_name(obj: Union[Namespace, Class]):
        if isinstance(obj, Namespace):
            return InterfaceGenerator._namespace_name(obj)
        elif isinstance(obj, Class):
            return InterfaceGenerator._class_name(obj)
        else:
            raise TypeError("Must be a class or a namespace")

    def _generate_creator(self, obj: Union[Class, Namespace]):
        name = self._obj_name(obj)

        with self._function_definition('create_{name}'.format(name=name), ['self']):
            self._return_statement('self.{name}()'.format(name=name))

    def _generate_namespace_initializer(self, namespace: Namespace):
        child_objects = namespace.namespaces + namespace.classes

        if not child_objects:
            return

        for obj in child_objects:
            self._generate_creator(obj)

        with self._function_definition('__init__', ['self']):
            for obj in child_objects:
                self._assign('self.{}'.format(obj.name),
                             'self.create_{}()'.format(self._obj_name(obj)))

    def _generate_class(self, klass: Class):
        with self._add_path(klass.name):
            with self._class_definition(self._class_name(klass)):
                self._generate_methods(klass.methods)
                self._generate_attributes(klass.attributes)

    def _generate_namespace(self, namespace: Namespace):
        with self._add_path(namespace.name):
            original_name, namespace.name = namespace.name, self._namespace_name(namespace)
            self._generate_interface(namespace)
            namespace.name = original_name

    def _generate_getters(self, objects: list):
        for obj in objects:
            self._generate_getter(obj)

    def _generate_getter(self, obj):
        with self._add_path(obj.name):
            with self._function_definition(obj.name):
                self._generate_getter_body(obj)

    def _generate_getter_body(self, obj):
        self._not_implemented_error()

    def _generate_methods(self, methods):
        for method in methods:
            self._generate_method(method)

    def _generate_method(self, method):
        self._generate_function(method, ['**kwargs'])

    def _generate_attributes(self, attributes):
        for attribute in attributes:
            self._generate_attribute(attribute)

    def _generate_attribute(self, attribute):
        self._generate_function(attribute)

    def _generate_function(self, obj: Union[Method, Attribute], arguments=None):
        with self._add_path(obj.name):
            self._generate_function_body(obj, arguments)

    def _generate_function_body(self, obj, arguments):
        with self._method_definition(obj.name, arguments):
            self._not_implemented_error()

    def _get_path_list(self):
        """
        Get the current path as a fragment list (e.g. ['path', 'to'])
        :return:
        """
        return self.current_path

    def _get_path_string(self):
        return '/'.join(self.current_path)
