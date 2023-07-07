import http.client as cli
from color import Color

def valid_word(word):
    return len(word) == 5 or len(word) == 7 or len(word) == 8

def get_colors(word):
    key = "happy"
    if len(word) == 7:
        key = "belated"
    elif len(word) == 8:
        key = "birthday"

    sols = [Color.GRAY for _ in word]
    
    freq_map = {}
    for k in key:
        freq_map[k] = freq_map.get(k, 0) + 1

    for i, (k, g) in enumerate(zip(key, word)):
        if k == g:
            sols[i] = Color.GREEN
            freq_map[k] -= 1

    for i, g in enumerate(word):
        if not sols[i] == Color.GREEN and freq_map.get(g, 0) > 0:
            freq_map[g] -= 1
            sols[i] = Color.YELLOW

    return sols

# # global client connection
# conn = cli.HTTPConnection("localhost:8008")
# 
# def valid_word(word):
#     conn.request("GET", "/validate", headers={"word": word})
#     response = conn.getresponse()
#     print(f"'{response.status}'")
#     print(f"'{response.read()}'")
# 
# def get_colors(word):
#     conn.request("GET", "/colors", headers={"word": word})
#     response = conn.getresponse()
#     print(f"'{response.status}'")
#     print(f"'{response.read()}'")

