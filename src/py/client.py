import http.client as cli
from app import App

# global client connection
conn = cli.HTTPConnection("localhost:8008")

def valid_word(word):
    conn.request("GET", "/validate", headers={"word": word})
    response = conn.getresponse()
    print(f"'{response.status}'")
    print(f"'{response.read()}'")

def get_colors(word):
    conn.request("GET", "/colors", headers={"word": word})
    response = conn.getresponse()
    print(f"'{response.status}'")
    print(f"'{response.read()}'")

