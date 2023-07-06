#ifndef WORDLE_H
#define WORDLE_H

#include <string>
#include "../../inc/json.hpp"
using json = nlohmann::json;

// state enum
enum State {GRAY, YELLOW, GREEN};

// to json and from_json methods
NLOHMANN_JSON_SERIALIZE_ENUM( State, {
    {GRAY, "GRAY"},
    {YELLOW, "YELLOW"},
    {GREEN, "GREEN"}
});

// declare the structs here
struct Word {
    int id;
    std::string word;
    unsigned int length;
    
    // constructors
    Word() = default;
    Word (std::string word, unsigned int length) : word(word), length(length) {}
    Word (std::string word) : word(word), length(word.size()) {}
    // to_json and from_json methods
    NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(Word, id, word, length);
};

struct WordHighlight {
    std::vector<State> colors;
    std::string word;
};

NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(WordHighlight, colors, word);

bool valid_word(Word guess);

WordHighlight get_colors(Word key, Word guess);

#endif
