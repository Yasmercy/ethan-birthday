import http.client as cli

# global client connection
conn = cli.HTTPSConnection("localhost:2222")

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

