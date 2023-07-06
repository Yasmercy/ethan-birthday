#define CPPHTTPLIB_OPENSSL_SUPPORT
#include <array>
#include "../../inc/httplib.h"
#include "../../inc/json.hpp"
#include "storage.h"
#include "wordle.h"

using json = nlohmann::json;
httplib::SSLServer svr("~/.ssh/cert.pem", "~/.ssh/key.pem");
std::array<std::string, 3> keys;

std::string get_key(unsigned int length) {
    return keys[(length == 7) + 2 * (length == 8)];
}

void get_valid_word(const httplib::Request& req, httplib::Response& res) {
    auto word = req.get_header_value("word");
    json j = valid_word(word);
    res.set_content(j.dump(), "text/plain");
}

void get_word_highlights(const httplib::Request& req, httplib::Response& res) {
    auto w = req.get_header_value("word");
    auto k = get_key(w.size());
    Word guess = Word {w};
    Word key = Word {k};
    json j = get_colors(key, guess);
    res.set_content(j.dump(), "text/plain");
}

void set_keys() {
    keys[0] = "happy";
    keys[1] = "belated";
    keys[2] = "birthday";
}

int main() {
    set_keys();
    svr.Get("/validate", get_valid_word);
    svr.Get("/colors", get_word_highlights);

    svr.listen("localhost", 8008);
}
