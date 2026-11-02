// The recompiled game code: a library built from the player's own game files (`make gen` + `make` in a source
// checkout, the start screen's setup otherwise; runtime/gamebuild.c) and loaded at startup (runtime/gamelib.c).
// Nothing from the game ships with the app.
#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "cpu.h"

#if defined(_WIN32)
#define GAMELIB_NAME "lasgame.dll"
#define GAMELIB_EXPORT __declspec(dllexport)
#elif defined(__APPLE__)
#define GAMELIB_NAME "lasgame.dylib"
#define GAMELIB_EXPORT __attribute__((visibility("default")))
#else
#define GAMELIB_NAME "lasgame.so"
#define GAMELIB_EXPORT __attribute__((visibility("default")))
#endif

// GAMELIB_ID (-D, from the Makefile): a hash of the generator and the headers the game code is compiled against.
#ifndef GAMELIB_ID
#define GAMELIB_ID "dev"
#endif

#define GAMELIB_ABI 1
#define GAMELIB_ABI_V2 2
#define GAMELIB_ABI_V3 3
#define GAMELIB_MAX_MODULES 4
#define GAMELIB_FULL_ID_SIZE 96

bool gamelib_old_cpu(void);  // runtime/gamelib.c: no AVX2 / FMA / BMI2 - the game code is built for x86-64-v2

// The id a library for the game files in game_dir has (GAMELIB_ID[-v2]-<build ID>); false when exefs/main is unreadable.
static inline bool gamelib_full_id(const char *game_dir, char *out, size_t size) {
    char path[1100];
    unsigned char hdr[0x60];
    snprintf(path, sizeof path, "%s/exefs/main", game_dir);
    FILE *f = fopen(path, "rb");
    if (!f) {
        snprintf(path, sizeof path, "%s/main", game_dir);
        f = fopen(path, "rb");
    }
    if (!f) return false;
    bool ok = fread(hdr, 1, sizeof hdr, f) == sizeof hdr && !memcmp(hdr, "NSO0", 4);
    fclose(f);
    if (!ok) return false;
    int n = snprintf(out, size, "%s%s-", GAMELIB_ID, gamelib_old_cpu() ? "-v2" : "");
    for (int i = 0; i < 8 && n + 2 < (int)size; i++) n += snprintf(out + n, size - n, "%02X", hdr[0x40 + i]);
    return true;
}

// Module descriptor
typedef struct {
    const char *name;
    const uint64_t *addrs;  // sorted guest addresses
    const GuestFn *fns;     // the functions at them
    const uint64_t *count;
} GameLibModule;

// ABI 1 struct (Link's Awakening / legacy Z-A)
typedef struct {
    uint32_t abi;
    const char *id;
    const uint64_t *main_addrs, *sdk_addrs;
    const GuestFn *main_fns, *sdk_fns;
    const uint64_t *main_count, *sdk_count;
} GameLibTablesV1;

// ABI 2 / ABI 3 struct (multi-module)
typedef struct {
    uint32_t abi;
    const char *id;
    uint32_t nmods;
    GameLibModule mods[GAMELIB_MAX_MODULES];
} GameLibTablesV3;

// Unified runtime tables struct
typedef struct {
    uint32_t abi;
    const char *id;
    uint32_t nmods;
    GameLibModule mods[GAMELIB_MAX_MODULES];
    // Legacy compatibility fields
    const uint64_t *main_addrs, *sdk_addrs;
    const GuestFn *main_fns, *sdk_fns;
    const uint64_t *main_count, *sdk_count;
} GameLibTables;

// The library's one exported function (tools/gamelib_entry.c).
typedef const void *(*GameLibEntry)(void);
#define GAMELIB_ENTRY "lasgame_tables"

#ifdef __cplusplus
extern "C" {
#endif

// Loads the game code for the game files in game_dir
bool gamelib_load(const char *game_dir, char *why, size_t why_size);
// The tables of the loaded library (NULL before gamelib_load succeeds).
const GameLibTables *gamelib_tables(void);
// True when a library usable with this build is in one of those places (without loading it).
bool gamelib_present(const char *game_dir);

#ifdef __cplusplus
}
#endif
