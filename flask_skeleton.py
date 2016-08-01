# -*- coding: utf-8 -*-

import sys
import os
import argparse
import jinja2
import codecs
import subprocess
import shutil

if sys.version_info < (3, 0):
    from shutilwhich import which
else:
    from shutil import which

import platform


# Globals #

cwd = os.getcwd()
script_dir = os.path.dirname(os.path.realpath(__file__))

# Jinja2 environment
template_loader = jinja2.FileSystemLoader(
    searchpath=os.path.join(script_dir, "templates"))
template_env = jinja2.Environment(loader=template_loader)


def get_arguments(argv):
    parser = argparse.ArgumentParser(description='Scaffold a Flask Skeleton.')
    parser.add_argument('appname', help='The application name')
    parser.add_argument('-s', '--skeleton', help='The skeleton folder to use.')
    parser.add_argument('-b', '--bower', help='Install dependencies via bower')
    parser.add_argument('-v', '--virtualenv', action='store_true')
    parser.add_argument('-g', '--git', action='store_true')
    args = parser.parse_args()
    return args


def generate_brief(args):
    template_var = {
        'pyversion': platform.python_version(),
        'appname': args.appname,
        'bower': args.bower,
        'virtualenv': args.virtualenv,
        'skeleton': args.skeleton,
        'path': os.path.join(cwd, args.appname),
        'git': args.git
    }
    template = template_env.get_template('brief.jinja2')
    return template.render(template_var)


def main(args):

    print("\nScaffolding...")

    # Variables #

    appname = args.appname
    fullpath = os.path.join(cwd, appname)
    skeleton_dir = args.skeleton

    # Tasks #

    # Copy files and folders
    print("Copying files and folders...")
    shutil.copytree(os.path.join(script_dir, skeleton_dir), fullpath)

    # Create config.py
    print("Creating the config...")
    secret_key = codecs.encode(os.urandom(32), 'hex').decode('utf-8')
    template = template_env.get_template('config.jinja2')
    template_var = {
        'secret_key': secret_key,
    }
    with open(os.path.join(fullpath, 'project', 'config.py'), 'w') as fd:
        fd.write(template.render(template_var))

    # Add bower dependencies
    if args.bower:
        print("Adding bower dependencies...")
        bower = args.bower.split(',')
        bower_exe = which('bower')
        if bower_exe:
            os.chdir(os.path.join(fullpath, 'project', 'client', 'static'))
            for dependency in bower:
                output, error = subprocess.Popen(
                    [bower_exe, 'install', dependency],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                ).communicate()
                if error:
                    print("An error occurred with Bower")
                    print(error)
        else:
            print("Could not find bower. Ignoring.")

    # Add a virtualenv
    virtualenv = args.virtualenv
    if virtualenv:
        print("Adding a virtualenv...")
        virtualenv_exe = which('pyvenv')
        if virtualenv_exe:
            output, error = subprocess.Popen(
                [virtualenv_exe, os.path.join(fullpath, 'env')],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            ).communicate()
            if error:
                with open('virtualenv_error.log', 'w') as fd:
                    fd.write(error.decode('utf-8'))
                    print("An error occurred with virtualenv")
                    sys.exit(2)
            venv_bin = os.path.join(fullpath, 'env/bin')
            output, error = subprocess.Popen(
                [
                    os.path.join(venv_bin, 'pip'),
                    'install',
                    '-r',
                    os.path.join(fullpath, 'requirements.txt')
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            ).communicate()
            if error:
                with open('pip_error.log', 'w') as fd:
                    fd.write(error.decode('utf-8'))
                    sys.exit(2)
        else:
            print("Could not find virtualenv executable. Ignoring")

    # Git init
    if args.git:
        print("Initializing Git...")
        output, error = subprocess.Popen(
            ['git', 'init', fullpath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ).communicate()
        if error:
            with open('git_error.log', 'w') as fd:
                fd.write(error.decode('utf-8'))
                print("Error with git init")
                sys.exit(2)
        shutil.copyfile(
            os.path.join(script_dir, 'templates', '.gitignore'),
            os.path.join(fullpath, '.gitignore')
        )


if __name__ == '__main__':
    arguments = get_arguments(sys.argv)
    print(generate_brief(arguments))
    main(arguments)
