#!/usr/local/bin/python

import click
import inquirer
from k8s.functions import Kuber
from cli import cli as cli
import pprint




    
if __name__ == '__main__':
    Kuber.load_kube_config()
    cli.choose_option()


    
