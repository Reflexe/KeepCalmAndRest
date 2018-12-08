import argparse

from parser.parser import Parser
from argparse import ArgumentParser, FileType
from os import path
import os
import logging
from importlib import import_module

logger = logging.getLogger(__name__)

logging.basicConfig()

logger.setLevel(logging.DEBUG)

generators = {
    'python-flask': import_module('generators.python.server_flask.main').ServerGenerator,
    'python-requests': import_module('generators.python.client-requests.main').ClientGenerator,
}


def write_generated_file(file, content, out_dir, update):
    if update:
        file_open_mode = 'w'
    else:
        file_open_mode = 'x'

    file_path = path.join(out_dir, file)
    file_dir = path.dirname(file_path)

    logger.info('writing {} to {}'.format(path.basename(file_path), file_path))

    os.makedirs(file_dir, exist_ok=True)
    with open(file_path, file_open_mode) as f:
        f.writelines((line + '\n' for line in content))


def main(args):
    parser = Parser()
    iface = parser.parse(args.specification.read())

    for generator in args.generators:
        for file_path, content in generator.generate(iface).items():
            write_generated_file(path.join(generator.name, file_path),
                                 content,
                                 args.out_directory,
                                 args.update)


def available_generators_keys_list():
    return tuple(generators.keys())


def generator_keys_to_modules(string: str):
    from re import findall, split

    # TODO: maybe we should drop element support and leave it to the user.
    # it has arguments
    if '(' in string:
        result = findall("(.+?)\((.+)\)", string)
        if not result or len(result[0]) != 2:
            raise argparse.ArgumentTypeError('Invalid generator expression: {}; '
                                             'The expression should look like "Class(Arg1, Arg2)"')

        key, arguments = result[0]
        arguments = split(', ?', arguments)
    else:
        key = string
        arguments = ()

    class_object = generators.get(key)
    if not class_object:
        raise argparse.ArgumentTypeError('Invalid generator: '
                                         '{}; choose one from: {}'.format(key,
                                                                          available_generators_keys_list()))

    try:
        return class_object(*arguments)
    except Exception as err:
        raise argparse.ArgumentTypeError('An error while evaluating '
                                         'the expression "{}": {}'.format(string,
                                                                          err))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('specification', type=FileType('r'))
    parser.add_argument('out_directory', type=str)
    parser.add_argument('--update', '-u', action='store_true', default=False)

    parser.add_argument('-g', '--add-generator', dest='generators',
                        # choices=available_generators_keys_list(),
                        action='append',
                        type=generator_keys_to_modules,
                        required=True)

    main(parser.parse_args())
