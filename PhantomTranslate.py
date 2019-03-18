#!/usr/bin/env python
import os
from optparse import OptionParser
import json


def create_dir(name):
    path = os.getcwd() + "/%s"%name
    try:
        os.mkdir(path)
    except OSError:
        print("Creation of the directory %s failed" % path)
    else:
        return path


usage = "usage: %prog [options] arg1 arg2"
parser = OptionParser(usage=usage)
parser.add_option("-i", "--input", dest="input", type="string", help="The path to the file to be converted.",
                  metavar="PATH")
parser.add_option("-o", "--output", dest="output", type="string",
                  help="The path to the file where the converted data should be saved.", metavar="PATH")
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", help="Outputs more for nerds.")
parser.add_option("-q", "--quiet", action="store_false", dest="verbose", help="Psst... [Default]", default=False)
(options, args) = parser.parse_args()

if len(vars(options)) < 1:
    parser.error("No argument specified")
if not options.input:
    parser.error("Input file must be specified")


verbose = options.verbose
_input = options.input
output = None
output_dict = dict()

if not os.path.isfile(_input):
    parser.error("Input file don't exists")
if not os.access(_input, os.R_OK):
    parser.error("Input file is not readable")
if not options.output:
    _in_split = _input.split("/")

    output = create_dir("output") + "/" + _in_split[-1][:-3] + ".json"
else:
    output = options.output

with open(_input) as f:
    content = f.readlines()
    content = [x.strip() for x in content]
    for line in content:
        if line[:2] == "$.":
            line = line.replace("$.lang.register(", "", 1).replace(");", "", 1)
            line = line.decode('string_escape')

            line = line.split(', ', 1)
            line = [e[1:-1] for e in line]
            output_dict[line[0]] = {"message": line[1].replace("(", "$").replace(")", "$")}
            if verbose:
                print("Converted language value: %s" % line[0])

with open(output, "w+") as f:
    f.write(json.dumps(output_dict, sort_keys=True, indent=4))

