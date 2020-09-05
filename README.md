# Manipulate Firefox Bookmarks

## Description

A command utility to convert a backup of Firefox bookmarks (JSON file) into
plain text, plain text with extra formatting, or markdown.

Output is to stdout and intended to be used in conjunction with file
redirection. e.g. `manipulate_firefox_bookmarks.py SOMETHING > FILE` on a POSIX
compliant OS (e.g. Linux, BSD, and MacOS) and
`manipulate_firefox_bookmarks.py SOMETHING | out-file FILE` on Windows 
(PowerShell).

## Requirements

- Python3
- Currently any OS (tested only on Linux). Future updates may be Linux only.

## Usage

Output a list of all bookmark titles to stdout:
```
./manipulate_firefox_bookmarks.py PATH_TO_BOOKMARKS_FILE
```

Output a list of all bookmarks titles to stdout with spaces for child objects:
```
./manipulate_firefox_bookmarks.py PATH_TO_BOOKMARKS_FILE --pretty_text spaces
```

Output a list of all bookmarks titles to stdout with tabs for child objects:
```
./manipulate_firefox_bookmarks.py PATH_TO_BOOKMARKS_FILE --pretty_text tabs
```

Convert the bookmarks to JSON and output to stdout, first heading is a h1:
```
./manipulate_firefox_bookmarks.py PATH_TO_BOOKMARKS_FILE --to_markdown 1
```
- `to_markdown` will accept 1 - 6 as an argument.

## Project Motivation

As someone on the operations side of IT, I find there is a lot of professional 
value in my bookmarks collection. 

When I find something of value, I want to find it again quickly and I don't 
want to waste a lot of time writing it down (unless there's value to that 
exercise). I find bookmarks are one of the better solutions to this problem.

However, I don't want that value to be locked into one medium or one company's
service (however great Mozilla may be).

Conversion to other mediums allows for extra value such as being able to use 
more powerful search functionality (e.g. grep, sed, awk, and fzf), access from
a terminal emulator, and access from networks where Firefox accounts are 
blocked.

## Design

A backup of Firefox bookmarks (JSON) is converted into a general tree
structure (GeneralTree). The GeneralTree is traversed and converted into
different formats using recursive instance methods.

A GeneralTree object represents the tree and holds most of the useful
methods to accomplish the applications end-goals. Each GeneralTree holds
references to a single Node and all child GeneralTrees (as a list).
The class has methods for conversion to markdown, text, and pretty
text (i.e. spacing). There is also a method to return all the bookmarks 
(as Node objects) as a list.

A Node object represents nodes on the tree and its function is to hold
data on each bookmark or bookmark container. Setter/getter methods and methods
to confirm that Node attributes match criteria.

Python 3 `argparse` is used to parse command-line arguments.

## Ideas For Extension

- Poll `places.sqlite` for changes and automate data conversion and file creation
  when changes are made.

- Add HTML as a conversion option. Allow tags, classes, and ids to be user 
  specified.

- Allow functionality for the output of objects, such that other Python 3 
  applications can use them.

- Flesh out the existing conversion options and make them more configurable.
