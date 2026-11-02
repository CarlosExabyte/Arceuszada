// Entry of the game code library (runtime/gamelib.h), compiled into it with the generated code: the function
// tables, found by name when the app loads the library. Everything else in it stays hidden.
#include "gamelib.h"

#if defined(GAMELIB_MULTI_MODULE) || defined(GAMELIB_ARCEUS)
#define MOD(n) extern const uint64_t n##_fn_addrs[], n##_fn_count; extern const GuestFn n##_fn_ptrs[];
MOD(main)
MOD(subsdk0)
MOD(subsdk1)
MOD(sdk)
#undef MOD

#define TAB(n) {#n, n##_fn_addrs, n##_fn_ptrs, &n##_fn_count}

GAMELIB_EXPORT const void *lasgame_tables(void) {
    static const GameLibTablesV3 t = {
        GAMELIB_ABI_V3,
        GAMELIB_ID,
        4,
        {
            TAB(main),
            TAB(subsdk0),
            TAB(subsdk1),
            TAB(sdk)
        }
    };
    return &t;
}
#else
extern const uint64_t main_fn_addrs[], sdk_fn_addrs[], main_fn_count, sdk_fn_count;
extern const GuestFn main_fn_ptrs[], sdk_fn_ptrs[];

GAMELIB_EXPORT const void *lasgame_tables(void) {
    static const GameLibTablesV1 t = {GAMELIB_ABI,  GAMELIB_ID,   main_fn_addrs,  sdk_fn_addrs,
                                      main_fn_ptrs, sdk_fn_ptrs,  &main_fn_count, &sdk_fn_count};
    return &t;
}
#endif
