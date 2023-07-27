import http.client as cli
from color import Color

# global client connection
conn = cli.HTTPSConnection("localhost:2222")

def valid_word(word):
    conn.request("GET", "/validate", headers={"word": word})
    response = conn.getresponse()
    return bool(response.read().decode())

def get_colors(word):
    conn.request("GET", "/colors", headers={"word": word})
    response = conn.getresponse()
    data = response.read().decode()
    colors = data[(data.index("[") + 1):(data.index("]"))].split(",")
    convert = {
        '"GREEN"': Color.GREEN,
        '"GRAY"': Color.GRAY,
        '"YELLOW"': Color.YELLOW
    }
    return [convert[color] for color in colors]

