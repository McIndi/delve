# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import argparse

from events.models import (
    FileUpload,
)

from .decorators import search_command

parser = argparse.ArgumentParser(
    prog="read_file",
    description="Read an uploaded file in as events.",
)
parser.add_argument(
    "filename",
    help="The uploaded file to read in.",
)
parser.add_argument(
    "--allow-escape",
    action="store_true",
    help="Allow automatic escaping file contents. ",
)
parser.add_argument(
    "--parse",
    choices=(
        "csv",
        "json",
        "jsonl",
        "xml",
    ),
    help="If specified, must be a supported option. File contents "
         "will be parsed according to the format specified.",
)

@search_command(parser)
def read_file(request, events, argv, environment):
    # import magic
    if events:
        raise ValueError("read_file must be the first search command")
    args = read_file.parser.parse_args(argv[1:])
    filename = args.filename
    file_object = FileUpload.objects.get(
        user=request.user,
        title=filename,
    )
    # file_type = magic.from_buffer(file_object.open("rb").read(2048))
    if args.parse:
        _format = args.parse
        if _format == "csv":
            import csv
            reader = csv.DictReader(file_object.content.open("r"))
            for row in reader:
                yield {
                    "title": file_object.title,
                    "url": file_object.content.url,
                    **row
                }
        elif _format == "json":
            import json
            content = json.load(file_object.content)
            if isinstance(content, (str, int, dict)):
                yield {
                    "title": file_object.title,
                    "url": file_object.content.url,
                    "content": content,
                }
            else:
                for item in content:
                    yield {
                        "title": file_object.title,
                        "url": file_object.content.url,
                        **item
                    }
        elif _format == "jsonl":
            import json
            for line in file_object.content:
                try:
                    content = json.loads(line)
                except:
                    if args.allow_escape:
                        try:
                            content = json.loads(line.replace("\\", "\\\\"))
                        except:
                            content = [line.decode()]
                    else:
                        content = [line.decode()]
                if isinstance(content, (str, int, dict)):
                    yield {
                        "title": file_object.title,
                        "url": file_object.content.url,
                        "content": content,
                    }
                else:
                    for item in content:
                        yield {
                            "title": file_object.title,
                            "url": file_object.content.url,
                            'content': item,
                        }
        elif _format == "xml":
            # from xml.etree.ElementTree import ElementTree as etree
            # tree = etree.parse
            import xmltodict
            import json
            dict_repr = xmltodict.parse(file_object.content, process_namespaces=False)
            yield json.loads(json.dumps(dict_repr))
        else:
            raise ValueError(f"Format {_format} is unsupported.")
    else:
        yield {
            "title": file_object.title,
            "url": file_object.content.url,
            "content": list(file_object.content),
        }
