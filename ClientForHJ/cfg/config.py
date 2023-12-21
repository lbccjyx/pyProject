import os

import yaml

import ClientForHJ.cfg.static as static

with open(static.resource_path(f"../cfg/config.yml"), 'r') as stream:
    content = yaml.safe_load(stream)
