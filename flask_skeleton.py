# -*- coding: utf-8 -*-

import sys
import os
import argparse
import shutil
import jinja2
import codecs
import subprocess

if sys.version_info < (3, 0):
    from shutilwhich import which
else:
    from shutil import which


# Globals #

cwd = os.getcwd()
script_dir = os.path.dirname(os.path.realpath(__file__))

# Jinja2 environment
template_loader = jinja2.FileSystemLoader(
    searchpath=os.path.join(script_dir, "templates"))
template_env = jinja2.Environment(loader=template_loader)


def main(argv):

    # Arguments #

    parser = argparse.ArgumentParser(description='Scaffold a Flask Skeleton.')
    parser.add_argument('appname', help='The application name')
    parser.add_argument('-s', '--skeleton', help='The skeleton folder to use.')
    parser.add_argument('-b', '--bower', help='Install dependencies via bower')
    args = parser.parse_args()

    # Variables #

    appname = args.appname
    fullpath = os.path.join(cwd, appname)
    skeleton_dir = args.skeleton

    # Tasks #

    # Copy files and folders
    shutil.copytree(os.path.join(script_dir, skeleton_dir), fullpath)

    # Create config.py
    secret_key = codecs.encode(os.urandom(32), 'hex').decode('utf-8')
    template = template_env.get_template('config.jinja2')
    template_var = {
        'secret_key': secret_key,
    }
    with open(os.path.join(fullpath, 'project', 'config.py'), 'w') as fd:
        fd.write(template.render(template_var))

    # Add bower dependencies
    if args.bower:
        bower = args.bower.split(',')
        bower_exe = which('bower')
        if bower_exe:
            os.chdir(os.path.join(fullpath, 'project', 'static'))
            for dependency in bower:
                output, error = subprocess.Popen(
                    [bower_exe, 'install', dependency],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                ).communicate()
                # print(output)
                if error:
                    print("An error occurred with Bower")
                    print(error)
        else:
            print("Could not find bower. Ignoring.")


if __name__ == '__main__':
    main(sys.argv)
