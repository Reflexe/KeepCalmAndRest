import json

from .classes import Interface, Namespace, Class, Attribute, Method, Argument


class Parser:
    """Parser the json according to the specs"""

    def __init__(self):
        pass

    class ParserError(RuntimeError):
        pass

    _STR_TYPE_TO_REAL = {
        'int': int,
        'dict': dict,
        'list': list,
    }

    def parse(self, input_str):
        try:
            obj = json.loads(input_str)
        except json.JSONDecodeError:
            raise Parser.ParserError("Not a valid json")

        if not isinstance(obj, dict):
            raise Parser.ParserError("The first object is not a dict")

        classes, namespaces, methods = self._check_elements(obj,
                                                            self.Element(name='classes', required=False, type=list),
                                                            self.Element(name='namespaces', required=False, type=list),
                                                            self.Element(name='methods', required=False, type=list))
        if classes:
            classes = self._parse_classes(classes)

        if namespaces:
            namespaces = self._parse_namespaces(namespaces)

        if methods:
            methods = self._parse_methods(methods)

        return Interface(classes=classes,
                         namespaces=namespaces,
                         methods=methods)

    def _parse_namespaces(self, namespaces):
        """
        Parse a list of namespaces
        :param namespaces: A list of objects.
        :return: /none
        """
        if not isinstance(namespaces, list):
            raise Parser.ParserError("Invalid namespaces list")

        for namespace in namespaces:
            yield self._parse_namespace(namespace)

    class Element:
        def __init__(self, **kwargs):
            self.name = kwargs['name']
            self.is_required = kwargs['required']
            self.type = kwargs['type']

    def _assert_type_is(self, obj, is_type):
        if not isinstance(obj, is_type):
            raise AssertionError("Invalid object: got {} instead of {}".format(str(type(obj)), str(is_type)))

    def _parse_namespace(self, namespace):
        if not isinstance(namespace, dict):
            raise Parser.ParserError("Namespace must be a dict")

        name, classes, methods, namespaces = self._check_elements(namespace,
                                                                  self.Element(name='name', required=True, type=str),
                                                                  self.Element(name='classes', required=False,
                                                                               type=list),
                                                                  self.Element(name='methods', required=False,
                                                                               type=list),
                                                                  self.Element(name='namespaces', required=False,
                                                                               type=list))

        if methods:
            methods = self._parse_methods(methods)

        if classes:
            classes = self._parse_classes(classes)

        if namespaces:
            namespaces = self._parse_namespaces(namespaces)

        return Namespace(name=name,
                         classes=classes,
                         methods=methods,
                         namespaces=namespaces)

    def _parse_methods(self, methods):
        self._assert_type_is(methods, list)
        for method in methods:
            yield self._parse_method(method)

    def _parse_method(self, method):
        self._assert_type_is(method, dict)

        name, arguments, return_type = self._check_elements(method,
                                                            self.Element(name='name', required=True, type=str),
                                                            self.Element(name='return_type', required=False, type=str),
                                                            self.Element(name='arguments', required=True, type=list))

        if return_type:
            return_type = self._parse_type(return_type)

        return Method(name=name,
                      return_value=return_type,
                      arguments=[self._parse_argument(argument) for argument in arguments])

    def _parse_argument(self, argument):
        self._assert_type_is(argument, dict)

        name, argument_type = self._check_elements(argument,
                                                   self.Element(name='name', required=True, type=str),
                                                   self.Element(name='type', required=False, type=str))

        argument_type = self._parse_type(argument_type)

        return Argument(name=name, type=argument_type)

    def _check_elements(self, obj: dict, *vargs):
        for element in vargs:
            if element.name not in obj:
                if element.is_required:
                    raise Parser.ParserError("Could not find element {}".format(element.name))
                else:
                    yield element.type()
            else:
                current_element = obj[element.name]
                if not isinstance(current_element, element.type):
                    raise Parser.ParserError(
                        "Invalid element type ({} instead of {})".format(str(type(current_element)),
                                                                         str(element.type)))
                yield current_element

    def _parse_type(self, str_type: str):
        self._assert_type_is(str_type, str)
        real_type = self._STR_TYPE_TO_REAL.get(str_type)

        if real_type:
            return real_type
        else:
            raise self.ParserError("Not a valid type")

    def _parse_classes(self, classes):
        self._assert_type_is(classes, list)

        for c in classes:
            yield self._parse_class(c)

    def _parse_class(self, c):
        self._assert_type_is(c, dict)

        name, methods, attributes = self._check_elements(c,
                                                         self.Element(name='name', required=True, type=str),
                                                         self.Element(name='methods', required=False, type=list),
                                                         self.Element(name='attributes', required=False, type=list))

        if methods:
            methods = self._parse_methods(methods)

        if attributes:
            attributes = self._parse_attributes(attributes)

        return Class(name=name, methods=methods, attributes=attributes)

    def _parse_attributes(self, attributes):
        for attribute in attributes:
            yield self._parse_attribute(attribute)

    def _parse_attribute(self, attribute):
        self._assert_type_is(attribute, dict)

        name, attr_type = self._check_elements(attribute,
                                               self.Element(name='name', required=True, type=str),
                                               self.Element(name='type', required=True, type=str))

        attr_type = self._parse_type(attr_type)

        return Attribute(name=name, type=attr_type)
