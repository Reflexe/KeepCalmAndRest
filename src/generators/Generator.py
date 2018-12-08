from parser.classes import Interface


class Generator:
    def __init__(self, module_name):
        self.name = module_name
        self.__current_file_contents = []
        self.__files = {}

    def print(self):
        for file in self.__files.values():
            if file:
                print('\n'.join(file))

    def files(self):
        return self.__files

    def generate(self, interface: Interface) -> dict:
        """
        Generate the set of files for that server.
        :param interface:
        :returns A filename->content dict.
        """
        raise NotImplementedError()

    def _not_implemented_error(self):
        self._add_line('raise NotImplementedError()')

    def _add_file(self, filename, content):
        self.__files[filename] = content

    def _add_files(self, files: dict):
        self.__files.update(files)

    def _set_current_file(self, path: str):
        """
        Replace the current file
        """
        self.__current_file_contents = []
        self._add_file(path, self.__current_file_contents)

    def _add_line(self, content: str):
        """Add line to the current file"""
        self.__current_file_contents.append(content)

    def _add_lines(self, lines: list):
        for line in lines:
            self._add_line(line)
