#ifndef STORAGE_H
#define STORAGE_H

#include "../../inc/sqlite_orm.h"
#include "wordle.h"

// declare the storage global variable
extern decltype(sqlite_orm::make_storage(
    "data/db.sqlite",
    sqlite_orm::make_table(
        "words",
        sqlite_orm::make_column("id", &Word::id, sqlite_orm::primary_key()),
        sqlite_orm::make_column("word", &Word::word),
        sqlite_orm::make_column("length", &Word::length)
    ))) storage;

// propagate the .sqlite file
// creates the db.csv file that is then imported into db.sqlite
void create_db_csv();

// clear the .sqlite file
void clear_db();
#endif
