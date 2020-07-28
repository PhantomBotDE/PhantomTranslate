#!/usr/bin/env python

# Copyright (c) 2020 phantombot.dev
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import os, sys, json

from optparse import OptionParser


def verbose_output(string):
    global verbose
    if verbose:
        print(string)


def replace_ph_var(string_item):
    if string_item.startswith("$") and string_item.endswith("$"):
        return "(" + string_item[1:-1] + ")"
    else:
        return string_item


def create_dir(name, cwd=True):
    if cwd:
        path = os.getcwd() + "/%s" % name
    else:
        path = name
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError:
            print("Creation of the directory %s failed" % path)
            exit(2)
        else:
            verbose_output("Output dir created.")
            return path
    else:
        verbose_output("Output dir already exists.")
        return path


def ph_to_i18n(file):
    global parser
    output_dict = dict()
    line_start = False
    content = file.readlines()
    content = [x.strip() for x in content]
    for line in content:
        if line.startswith("$.lang.register"):
            line_start = True
            break
        else:
            line_start = False

    if not line_start:
        parser.error("This is not a PhantomBot lang file.")
        exit(2)
    else:
        verbose_output("PhantomBot lang file identified")

    for line in content:
        if line[:2] == "$.":
            line = line.replace("$.lang.register(", "", 1).replace(");", "", 1)
            line = line.decode('string_escape')

            line = line.split(', ', 1)
            line = [e[1:-1] for e in line]
            output_dict[line[0]] = {"message": line[1]}
            if verbose:
                verbose_output("Converted language value: %s" % line[0])
    return json.dumps(output_dict, sort_keys=True, indent=4)


def i18n_to_ph(file):
    global parser
    json_object = None
    try:
        json_object = json.loads(file.read())
        verbose_output("i18n JSON file identified and imported.")
    except ValueError:
        parser.error("This is not a valid JSON file.")
    itemiter = json_object.items()
    output = ""
    for item in itemiter:
        message = item[1]["message"].encode('utf-8')
        word_list = message.split()

        # word_list = [replace_ph_var(word) for word in word_list]
        ph_string = ' '.join(word for word in word_list)
        output += "$.lang.register(\'" + str(item[0]) + "\', \'" + ph_string.replace("'", r"\'") + "\');\n\r"
        verbose_output("Added \"%s\" for PhantomBot lang file" % str(item[0]))
    return output


def get_file_structure(start_path=os.getcwd()):
    if start_path[-1] != '/':
        start_path += "/"
    files_structure = []
    for root, dirs, files in os.walk(start_path, ):
        root = root.replace(start_path, '')
        for name in files:
            tmp = name.split('.')
            if tmp[-1] == "js" or tmp[-1] == "json":
                files_structure.append(os.path.join(root, name).split("/"))
    return files_structure


usage = "usage: %prog [options] arg1 arg2"
parser = OptionParser(usage=usage)
parser.add_option("-i", "--input", dest="input", type="string", help="The path to the file to be converted.",
                  metavar="PATH")
parser.add_option("-o", "--output", dest="output", type="string",
                  help="The path to the file where the converted data should be saved.", metavar="PATH")
parser.add_option("-f", "--format", dest="format_type", type="choice", choices=["i18n", "ph", "phantombot"],
                  help="Choose the input file type, if it is a i18n file or an phantombot lang file",
                  metavar="i18n / ph")
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", help="Outputs more for nerds.")
parser.add_option("-q", "--quiet", action="store_false", dest="verbose", help="Psst... [Default]", default=False)
parser.add_option("-t", "--type", dest="input_type", type="choice", choices=["f", "d"],
                  help="Choose the if the input is a file or an dir.", metavar="f / d", default="d")
(options, args) = parser.parse_args()

if len(vars(options)) < 1:
    parser.error("No argument specified")
if not options.input:
    parser.error("Input file must be specified")
elif not options.format_type:
    parser.error("Input file format not specified")

verbose = options.verbose
_input = options.input
output = None
if options.format_type == "i18n":
    format_type = "i18n"
else:
    format_type = "ph"

if options.input_type == "f":
    if not os.path.isfile(_input):
        parser.error("Input file don't exists")
    if not os.access(_input, os.R_OK):
        parser.error("Input file is not readable")
    if not options.output:
        _in_split = _input.split("/")
        if format_type == "i18n":
            output = create_dir("output") + "/" + _in_split[-1][:-5] + ".js"
        else:
            output = create_dir("output") + "/" + _in_split[-1][:-3] + ".json"

    else:
        output = options.output

    file_output = None
    with open(_input) as f:
        if format_type == "i18n":
            file_output = i18n_to_ph(f)
        else:
            file_output = ph_to_i18n(f)
    if format_type == "i18n":
        file_output = "/*\n\r" \
                      " * Copyright (C) 2016-2020 phantombot.dev\n\r" \
                      " *\n\r" \
                      " * This program is free software: you can redistribute it and/or modify\n\r" \
                      " * it under the terms of the GNU General Public License as published by\n\r" \
                      " * the Free Software Foundation, either version 3 of the License, or\n\r" \
                      " * (at your option) any later version.\n\r" \
                      " *\n\r" \
                      " * This program is distributed in the hope that it will be useful,\n\r" \
                      " * but WITHOUT ANY WARRANTY; without even the implied warranty of\n\r" \
                      " * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n\r" \
                      " * GNU General Public License for more details.\n\r" \
                      " *\n\r" \
                      " * You should have received a copy of the GNU General Public License\n\r" \
                      " * along with this program.  If not, see <http://www.gnu.org/licenses/>.\n\r" \
                      " */\n\r\n\r" + file_output

    with open(output, "w+") as f:
        print("File converted")
        f.write(file_output)

else:

    if _input[-1] != '/':
        _input += "/"
    output = None
    if not options.output:
        output = create_dir("output")
    else:
        output = options.output
    for structure in get_file_structure(_input):
        backup = list(structure)

        file_output = None
        if not format_type == "i18n":
            structure[-1] = "_".join(structure)
        else:
            structure = structure[-1].split("_")
        original_file = _input + "/".join(backup)
        verbose_output(original_file)
        with open(original_file) as f:
            if format_type == "i18n":
                file_output = i18n_to_ph(f)
            else:
                file_output = ph_to_i18n(f)
        _output = output
        if structure[:-1]:
            _output = create_dir(output + "/" + "/".join(structure[:-1]), False)
        filename = None
        if format_type == "i18n":
            file_output = "/*\n\r" \
                          " * Copyright (C) 2016-2020 phantombot.dev\n\r" \
                          " *\n\r" \
                          " * This program is free software: you can redistribute it and/or modify\n\r" \
                          " * it under the terms of the GNU General Public License as published by\n\r" \
                          " * the Free Software Foundation, either version 3 of the License, or\n\r" \
                          " * (at your option) any later version.\n\r" \
                          " *\n\r" \
                          " * This program is distributed in the hope that it will be useful,\n\r" \
                          " * but WITHOUT ANY WARRANTY; without even the implied warranty of\n\r" \
                          " * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n\r" \
                          " * GNU General Public License for more details.\n\r" \
                          " *\n\r" \
                          " * You should have received a copy of the GNU General Public License\n\r" \
                          " * along with this program.  If not, see <http://www.gnu.org/licenses/>.\n\r" \
                          " */\n\r\n\r" + file_output
            with open(_output + "/" + structure[-1][:-5] + ".js", "w+") as f:
                verbose_output("File converted")
                f.write(file_output)
                filename = f.name
        else:
            with open(_output + "/" + structure[-1][:-3] + ".json", "w+") as f:
                verbose_output("File converted")
                f.write(file_output)
                filename = f.name
        if sys.platform == "linux":
            os.system("unix2dos -o " + filename)
            verbose_output("Converted file to dos format: " + filename)
    print("All converted.")
