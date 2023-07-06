#include "../../inc/sqlite_orm.h"
#include "wordle.h"

using namespace sqlite_orm;

auto storage = sqlite_orm::make_storage(
    "data/db.sqlite",
    sqlite_orm::make_table(
        "words",
        sqlite_orm::make_column("id", &Word::id, sqlite_orm::primary_key()),
        sqlite_orm::make_column("word", &Word::word),
        sqlite_orm::make_column("length", &Word::length)
    )
);

void create_db_csv() {}
void clear_db() {}
