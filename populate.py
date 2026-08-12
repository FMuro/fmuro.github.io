#!.venv/bin/python3

import yaml  # YAML parsing
from jinja2 import Environment, FileSystemLoader  # Jinja template

# Folder with data and templates and do extension
ENV = Environment(loader=FileSystemLoader('.'), extensions=['jinja2.ext.do'])


# jinja2 template

web_template = ENV.get_template('src/pug/index.j2') # landing page

# Opening the data files
with open("output.yaml") as y:
    with open("data.yml") as z:
        # Loading the YAML data
        biblio = yaml.load(y, Loader=yaml.BaseLoader)['result']
        for entry in biblio:
            print(entry.keys())
        datos = yaml.load(z, Loader=yaml.BaseLoader)
        # Opening the output files
        f = open('src/pug/index.pug', 'w', encoding="utf8")
        # Rendering the output files from data, biblio and jinja2 templates
        output = web_template.render(biblio=biblio, datos=datos)
        # Writing to the output files
        f.write(output)
        # Closing the output files
        f.close()