#!/bin/bash

pybabel extract . -o locale/template.pot
pybabel update -i locale/template.pot -o locale/en_GB/LC_MESSAGES/messages.po -l "en_GB"
pybabel update -i locale/template.pot -o locale/it_IT/LC_MESSAGES/messages.po -l "it_IT"
pybabel compile -d locale