# -*- coding: utf-8 -*-

__author__ = "Massimo Guidi"
__author_email__ = "maxg1972@gmail.com"
__version__ = "1.0"
__python_version__ = "3.8"

import argparse
import os
import sys
from pathlib import Path

from github import Github


class Options(argparse.ArgumentParser):
    """Extends argparse.ArgumentParser to handle errors
    """
    def error(self, message):
        script_name = os.path.splitext(os.path.basename(__file__))[0]
        sys.stderr.write("%s: %s. Use '%s --help'\n" % (script_name, message, script_name))
        #self.print_help()
        sys.exit(2)


def get_arguments() -> Options:
    """Define the script options, read the command line arguments 
    
    Returns:
        Options -- strinpt options
    """
    # Get script arguments
    opts = Options(description="Create new python project structure")
    opts.add_argument("project_name", action="store", help="project name")
    opts.add_argument("--django", action="store_true", dest="django", help="create a Django project", default=False)
    opts.add_argument("--github", action="store_true", dest="github", help="create a github repository", default=False)
    opts.add_argument("--no-venv", action="store_true", dest="no_venv", help="not use virtualenv environment", default=False)

    args = opts.parse_args()

    return args


def github_conn():
    token_file = "%s/.config/pycreate/config" % Path.home()
    
    with open(token_file, 'r') as cfg_file:
        token = cfg_file.read().replace("\n", "")

    return Github(token)

def create_project(opts: Options):
    dest_path = os.getcwd() + f"/{opts.project_name}"

    commands = []
    if opts.github:
        gh = github_conn()        

        # get or create repository
        new = False
        user = gh.get_user()
        try:
            user.get_repo(opts.project_name)
            new = True
        except:
            repo = user.create_repo(opts.project_name)

        # clone repository
        os.system(f"git clone git@github.com:{user.login}/{opts.projecy_name}.git")

        commands.extend( 
            [
                f"@echo # {opts.projecy_name}>> README.md",
                "@echo venv/ >> .gitignore",
                "@echo .vscode/ >> .gitignore",
                "git add .",
                'git commit -m "Initial commit"',
                "git push -u origin master",
            ]
        )
    else:
        os.mkdir(dest_path)

    os.chdir(dest_path)

    if not opts.no_venv:
        commands.append("virtualenv venv")
    
    if opts.django:
        commands.extend( 
            [
                "source venv/bin/activate ",
                "pip3 install Django",
                f"django-admin.py startproject {opts.projecy_name}",
                "deactivate",
            ]
        )

        dest_path = dest_path + f"/{opts.project_name}"
    
    commands.append("code .")
    for c in commands:
        os.system(c)    


if __name__ == "__main__":
    opts = get_arguments()
    create_project(opts)
