#include <catch2/catch_test_macros.hpp>
#include "../src/cxx/wordle.h"


TEST_CASE ("wordle-highlights no repeats", "[get_colors]") {
    auto key = Word("venom", 5);
    std::vector<State> sol;
    
    // venom --> [g, g, g, g, g]
    auto venom = get_colors(key, Word("venom", 5));
    sol = {GREEN, GREEN, GREEN, GREEN, GREEN};
    REQUIRE (venom.colors == sol);
    REQUIRE (venom.word.word == "venom");

    // swear --> [r, r, y, r, r]
    auto swear = get_colors(key, Word("swear", 5));
    sol = {GRAY, GRAY, YELLOW, GRAY, GRAY};
    REQUIRE (swear.colors == sol);  
    REQUIRE (swear.word.word == "swear");

    // count --> [r, y, r, y, r]
    auto count = get_colors(key, Word("count", 5));
    sol = {GRAY, YELLOW, GRAY, YELLOW, GRAY};
    REQUIRE (count.colors == sol);  
    REQUIRE (count.word.word == "count");
}

TEST_CASE ("wordle-highlights repeats", "[get_colors]") {
    auto key = Word("venom", 5);
    std::vector<State> sol;
    
    // venom --> [g, g, g, g, g]
    auto venom = get_colors(key, Word("venom", 5));
    sol = {GREEN, GREEN, GREEN, GREEN, GREEN};
    REQUIRE (venom.colors == sol);
    REQUIRE (venom.word.word == "venom");

    // teeth --> [r, g, r, r, r]
    auto teeth = get_colors(key, Word("teeth", 5));
    sol = {GRAY, GREEN, GRAY, GRAY, GRAY};
    REQUIRE (teeth.colors == sol);  
    REQUIRE (teeth.word.word == "teeth");

    // breed --> [r, r, y, r, r]
    auto breed = get_colors(key, Word("breed", 5));
    sol = {GRAY, GRAY, YELLOW, GRAY, GRAY};
    REQUIRE (breed.colors == sol);  
    REQUIRE (breed.word.word == "breed");
}

TEST_CASE ("wordle valid words (5 letters)", "[valid_word]") {
    REQUIRE (valid_word(Word("venom", 5)));
    REQUIRE (valid_word(Word("timer", 5)));
    REQUIRE (valid_word(Word("swear", 5)));
    REQUIRE (!valid_word(Word("VENOM", 5)));
    REQUIRE (!valid_word(Word("abcde", 5)));
    REQUIRE (!valid_word(Word("aaaaa", 5)));
}


TEST_CASE ("wordle valid words (7 letters)", "[valid_word]") {

}

TEST_CASE ("wordle valid words (8 letters)", "[valid_word]") {

}

TEST_CASE ("json for word highlight", "[to_json, from_json]") {

}
