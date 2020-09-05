#!/usr/bin/env python3

'''
    Converts a backup of Firefox bookmarks (JSON) into a general tree
    structure. There are methods for conversion to markdown, text, and pretty
    text (i.e. spacing).

    Output is to stdout and intended to be used in conjunction with file
    redirection. e.g. `parse_bookmarks.py SOMETHING > FILE` on a POSIX
    compliant OS and `parse_bookmarks.py SOMETHING | out-file FILE` on
    Windows.

    There is also a method to return all the bookmarks (as Node objects) as a
    list.

    This is all accomplished using two main objects.

    A GeneralTree object represents the tree and holds most of the useful
    methods to accomplish the applications end-goals.

    A Node object represents nodes on the tree and its function is to hold
    data on each bookmark or bookmark container.
'''

import json
import argparse
import sys

# Section 1: Parse Arguments with `argparse`

parser = argparse.ArgumentParser("Manipualtes Firefox bookmarks JSON in various ways. Default "
                                 + "behaviour is to output a list of bookmark/folder titles with "
                                 + "no special formatting.")

parser.add_argument("FILE", help="The bookmarks file to parse.")

parser.add_argument("--to_markdown",
                    help="Convert the bookmarks file to markdown. The value is the initial"
                    + " header level. Outputs to stdout.",
                    metavar="1-6",
                    required=False,
                    choices=range(1, 6),
                    type=int)

parser.add_argument("--pretty_text",
                    help="Output the bookmarks file as plain text with spaces or tabs to show"
                    + " children. Outputs to stdout.",
                    metavar="{spaces|tabs}",
                    required=False,
                    choices=["spaces", "tabs"])

args = parser.parse_args()

# Section 2: ADTs

class Node:
    '''
    A node of a GeneralTree. Each node represents a bookmark or bookmark
    container.
    '''

    def __init__(self):
        self.guid = None
        self.title = None
        self.index = None
        self.date_added = None
        self.last_modified = None
        self.identity = None
        self.type_ = None
        self.type_code = None
        self.root = None
        self.uri = None
        self.guid_of_parent = None

    def set_guid(self, guid):
        self.guid = guid

    def get_guid(self):
        return self.guid

    def set_title(self, title):
        self.title = title

    def get_title(self):
        return self.title

    def set_index(self, index):
        self.index = index

    def get_index(self):
        return self.index

    def set_date_added(self, date_added):
        self.date_added = date_added

    def get_date_added(self):
        return self.date_added

    def set_last_modified(self, last_modified):
        self.last_modified = last_modified

    def get_last_modified(self):
        return self.last_modified

    def set_id(self, identity):
        self.identity = identity

    def get_id(self):
        return self.identity

    def set_type_code(self, type_code):
        self.type_code = type_code

    def get_type_code(self):
        return self.type_code

    def set_type(self, type_):
        self.type_ = type_

    def get_type(self):
        return self.type_

    def set_root(self, root):
        self.root = root

    def get_root(self):
        return self.root

    def set_uri(self, uri):
        self.uri = uri

    def get_uri(self):
        return self.uri

    def is_folder(self):
        return self.type_ == "text/x-moz-place-container"

    def set_parent_guid(self, guid):
        self.guid_of_parent = guid

    def get_parent_guid(self):
        return self.guid_of_parent


class GeneralTree:
    '''
        Takes Firefox JSON bookmarks data and converts it into a general tree
        data structure. The structure is created in init using recursion.
        GeneralTree holds a reference (self.node) to the current node (Node
        object) and list of child GeneralTrees (self.children). All actual
        data is held with Node objects.
    '''

    def __init__(self, exportedJSON, parentGUID):
        '''
            exportedJSON = the bookmarks JSON exported from Firefox.
            parentGUID = the GUID of the parent. Should be None for the
                initial call.
        '''

        self.node = Node()
        self.children = []
        child_value = ""  # Temporary to hold any children we find
        if parentGUID is not None:  # Assuming None implies the root node
            self.node.set_parent_guid(parentGUID)
        for key, value in exportedJSON.items():
            if key == "guid":
                self.node.set_guid(value)
            if key == "title":
                self.node.set_title(value)
            if key == "index":
                self.node.set_index(value)
            if key == "dateAdded":
                self.node.set_date_added(value)
            if key == "lastModified":
                self.node.set_last_modified(value)
            if key == "typeCode":
                self.node.set_type_code(value)
            if key == "type":
                self.node.set_type(value)
            if key == "root":
                self.node.set_root(value)
            if key == "uri":
                self.node.set_uri(value)
            if key == "id":
                self.node.set_id(value)
            if key == "children":
                child_value = value
        for item in child_value:
            self.children.append(GeneralTree(item, self.node.get_guid()))

    def has_children(self):
        return len(self.children) > 0

    def print_all_titles(self):
        '''
            Print the titles of all bookmarks and containers. Includes
            containers usually abstracted away from a Firefox user,
            e.g. root.
        '''

        print(self.node.get_title())
        for child in self.children:
            child.print_all_titles()

    def return_all_nodes(self):
        '''
            Return a list of Nodes in the tree as list.
        '''

        nodes = []
        nodes.append(self.node)
        for child in self.children:
            nodes.append(child.return_all_nodes())
        return nodes

    def print_all_titles_spacer(self, initial_spacer, spacer):
        '''
            Outputs titles with an additional spacer for the contents of each subfolder.
                initial_spacer  = starting whitespace
                spacer          = whitespace to add for children of each subfolder
        '''

        if self.node.get_title() == "":  # Assuming the only empty title is root
            print("root")
        else:
            print(initial_spacer + self.node.get_title())
        if self.has_children():
            for child in self.children:
                child.print_all_titles_spacer(initial_spacer + spacer, spacer)
        else:
            for child in self.children:
                child.print_all_titles_spacer(initial_spacer, spacer)

    def to_markdown(self, header):
        '''
            Converts the tree structure into markdown and outputs it to stdout.

            Containers become headings. Each subcontainer becomes a
            lower-level heading. i.e. a child of a H1 folder will become a H2.

            Links become lists of hyperlinks.

            Containers are processed after links because otherwise the contents
            of parent folders can visually appear under that of subfolders.

            header is an int representing the level of header to start with.
        '''

        folders = []
        if self.node.is_folder():
            print('')
            for i in range(header):
                print('#', end='')
            print(' ', end='')
            if self.node.get_title() == "":
                print("root")
            else:
                print(escape_vertical_bars(self.node.get_title()))
            print('')
            header += 1
            if len(self.children) > 0:
                for child in self.children:
                    if child.node.is_folder():
                        folders.append(child)
                    else:
                        child.to_markdown(header)
                for child in folders:
                    child.to_markdown(header)
        else:
            print('- [' + escape_vertical_bars(self.node.get_title())
                  + '](' + self.node.get_uri() + ')')

# Section 3: Helper Functions

def escape_vertical_bars(input_string):
    ''' Escape vertical bars to stop markdown parsers confusing them with tables. '''
    return input_string.replace("|", "\\|")

# Section 4: Initialisation and Validation

# The args object is the end result of processing arguments in Section 1.
# An attribute on args is created for each command-line argument:
#   to_markdown, pretty_text, and FILE
# If an argument is not set, the value is None.

try:
    with open(args.FILE) as f:
        data = json.load(f)
except FileNotFoundError:
    print("The specified file does not exist.")
    sys.exit(1)
except PermissionError:
    print("The program does not have permission to read the specified file.")
    sys.exit(1)

bookmarks = GeneralTree(data, None)

if args.pretty_text is not None and args.to_markdown is not None:
    print("Please choose --pretty_text or --to_markdown, not both.")
    sys.exit(1)
elif args.to_markdown is not None:
    bookmarks.to_markdown(args.to_markdown)
elif args.pretty_text is not None:
    if args.pretty_text == "spaces":
        bookmarks.print_all_titles_spacer("", " ")
    elif args.pretty_text == "tabs":
        bookmarks.print_all_titles_spacer("", "\t")
else:
    bookmarks.print_all_titles()
