#!/usr/bin/env bash

mkdir -p ~/.streamlit/

echo -e "\
[general]\n\
email = \"tommaso.bonomo.97@gmail.com\"\n\
" > ~/.streamlit/credentials.toml

echo -e "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml
