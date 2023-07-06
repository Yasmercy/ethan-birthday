#include <vector>
#include <unordered_map>
#include "../../inc/sqlite_orm.h"
#include "wordle.h"
#include "storage.h"

// helper functions
std::unordered_map<char, int> freq_map(std::string word) {
    std::unordered_map<char, int> map;
    for (char c : word) ++map[c];
    return map;
}

std::vector<State> get_color_vec(std::string guess, std::string key, unsigned int length) {
    std::vector<State> colors(length);
    auto map = freq_map(key);

    // mark all greens (and update map)
    for (unsigned int i = 0; i < length; ++i) {
        if (key[i] == guess[i]) {
            colors[i] = State::GREEN;
            --map[guess[i]];
        }
    }

    // mark all yellows
    for (unsigned int i = 0; i < length; ++i) {
        if (colors[i] != State::GREEN && --map[guess[i]] >= 0) {
            colors[i] = State::YELLOW;
        }
    }
    return colors;
}

// functions
bool valid_word(Word guess) {
    using namespace sqlite_orm;
    auto word = storage.get_all<Word>(where(c(&Word::word) == guess.word));
    return word.size() != 0;
}

WordHighlight get_colors(Word key, Word guess) {
    return WordHighlight {
        get_color_vec(guess.word, key.word, key.length),
        guess
    };
}

