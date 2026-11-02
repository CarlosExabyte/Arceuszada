#!/usr/bin/env python3
"""
Pokemon Legends: Arceus Recomp - Multi-Module Recompilation Orchestrator
Lifts ARM64 NSO binaries, compiles generated C chunks with Zig, and links lasgame.dll.
"""

import os
import sys
import time
import shutil
import argparse
import subprocess
import concurrent.futures

MODULES = [
    {"name": "main",    "file": "main",    "base": "0x7100000000"},
    {"name": "subsdk0", "file": "subsdk0", "base": "0x7104800000"},
    {"name": "subsdk1", "file": "subsdk1", "base": "0x7105000000"},
    {"name": "sdk",     "file": "sdk",     "base": "0x7106000000"},
]

def run_cmd(cmd, desc=""):
    t0 = time.time()
    res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    dt = time.time() - t0
    if res.returncode != 0:
        print(f"\n[FALHA] {desc} (em {dt:.1f}s)")
        print(res.stdout[-2000:])
        return False
    return True

def is_cold_giant(src_path):
    try:
        if os.path.getsize(src_path) > 150 * 1024:
            return True
        with open(src_path, "r", encoding="latin1") as f:
            lines = 0
            for line in f:
                lines += 1
                if lines > 1500:
                    return True
    except Exception:
        pass
    return False

def compile_c_file(zig_exe, src_path, obj_path, inc_dir):
    if os.path.exists(obj_path) and os.path.getmtime(obj_path) >= os.path.getmtime(src_path):
        return True, src_path, ""
    giant = is_cold_giant(src_path)
    opt = "-O0" if giant else "-O1"
    cmd = [
        zig_exe, "cc", "-c", src_path,
        "-I", inc_dir,
        "-target", "x86_64-windows-gnu",
        opt, "-DGUEST_VOLATILE",
        "-DGAMELIB_MULTI_MODULE",
    ]
    if giant:
        cmd.extend(["-fno-sanitize=all", "-fno-stack-protector"])
    cmd.extend(["-o", obj_path])
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return res.returncode == 0, src_path, res.stdout

def build_recomp(test_mode=False, limit=50, max_workers=None, force_gen=False):
    proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    exefs_dir = os.path.join(proj_root, "extracted", "exefs")
    gen_dir = os.path.join(proj_root, "build", "generated")
    obj_dir = os.path.join(proj_root, "build", "obj")
    gamelib_dir = os.path.join(proj_root, "gamelib-src")
    lasgen_exe = os.path.join(proj_root, "lasgen", "lasgen.exe")
    zig_exe = os.path.join(proj_root, "zig", "zig.exe")
    zig_rt = os.path.join(proj_root, "zig", "rt")
    out_dll = os.path.join(proj_root, "extracted", "lasgame.dll")
    out_id = os.path.join(proj_root, "extracted", "lasgame.dll.id")
    import_lib = os.path.join(proj_root, "lasrecomp.dll.a")

    print("\n==========================================================")
    print(" POKÉMON LEGENDS: ARCEUS RECOMP - COMPILADOR NATIVO")
    print(f" Modo: {'TESTE RÁPIDO (limite: ' + str(limit) + ' funções/módulo)' if test_mode else 'RECOMPILAÇÃO COMPLETA'}")
    print("==========================================================\n")

    os.makedirs(gen_dir, exist_ok=True)
    os.makedirs(obj_dir, exist_ok=True)

    # 1. Checar ferramentas
    if not os.path.exists(lasgen_exe):
        print(f"[ERRO] lasgen.exe não encontrado em: {lasgen_exe}")
        return False
    if not os.path.exists(zig_exe):
        print(f"[ERRO] zig.exe não encontrado em: {zig_exe}")
        return False

    # 2. Lift dos 4 módulos com lasgen
    print("[FASE 1/3] Traduzindo instruções ARM64 para C nativo (lasgen)...")
    t_start = time.time()
    all_tables = all(os.path.exists(os.path.join(gen_dir, f"{m['name']}_table.c")) for m in MODULES)
    if all_tables and not test_mode and not force_gen:
        print("  -> Chunks C já gerados para todos os 4 módulos. Reutilizando build/generated...")
    else:
        for m in MODULES:
            nso_path = os.path.join(exefs_dir, m["file"])
            if not os.path.exists(nso_path):
                print(f"[ERRO] Módulo não encontrado em extracted/exefs: {m['file']}")
                return False

            cmd = f'"{lasgen_exe}" {m["name"]} "{nso_path}" {m["base"]} "{gen_dir}"'
            if test_mode:
                cmd += f' --limit {limit}'

            print(f"  -> Traduzindo {m['name']} (base {m['base']})...", end="", flush=True)
            t_mod = time.time()
            ok = run_cmd(cmd, f"Lifting do módulo {m['name']}")
            if not ok:
                return False
            print(f" [OK] ({time.time() - t_mod:.1f}s)")

    # 2.5 Se modo teste, gerar stubs para funções além do limite
    if test_mode:
        import re
        declared = set()
        defined = set()
        for f in os.listdir(gen_dir):
            if f.endswith(".c") and f != "test_stubs.c":
                with open(os.path.join(gen_dir, f), "r", encoding="latin1") as fp:
                    cnt = fp.read()
                for m in re.finditer(r'void\s+(f_[0-9a-fA-F]+)\s*\(\s*Cpu\s*\*c\s*\)\s*\{', cnt):
                    defined.add(m.group(1))
                for m in re.finditer(r'void\s+(f_[0-9a-fA-F]+)\s*\(\s*Cpu\s*\*c\s*\)\s*;', cnt):
                    declared.add(m.group(1))
        missing = sorted(list(declared - defined))
        if missing:
            stubs_path = os.path.join(gen_dir, "test_stubs.c")
            with open(stubs_path, "w", encoding="ascii") as fp:
                fp.write('#include "cpu.h"\n')
                for fn in missing:
                    fp.write(f'void {fn}(Cpu *c) {{}}\n')
            print(f"  [TESTE] Gerados stubs para {len(missing)} funções fora do limite de teste.")

    # 3. Compilar todos os .c gerados + gamelib_entry.c com Zig em paralelo
    print("\n[FASE 2/3] Compilando código C com Clang/Zig (x86-64-v3 / AVX2)...")
    c_files = []
    for f in os.listdir(gen_dir):
        if f.endswith(".c"):
            c_files.append(os.path.join(gen_dir, f))
    c_files.append(os.path.join(gamelib_dir, "gamelib_entry.c"))

    total_files = len(c_files)
    print(f"  Total de unidades de compilação: {total_files} arquivos")

    workers = max_workers or min(os.cpu_count() or 4, 16)
    print(f"  Executando em paralelo com {workers} threads...")

    t_comp = time.time()
    obj_files = []
    failed = False

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {}
        for c in c_files:
            bname = os.path.splitext(os.path.basename(c))[0] + ".obj"
            obj_path = os.path.join(obj_dir, bname)
            obj_files.append(obj_path)
            f = executor.submit(compile_c_file, zig_exe, c, obj_path, gamelib_dir)
            futures[f] = c

        done_cnt = 0
        for f in concurrent.futures.as_completed(futures):
            ok, src, out = f.result()
            done_cnt += 1
            if not ok:
                print(f"\n[ERRO] Falha ao compilar: {src}\n{out}")
                failed = True
                break
            if done_cnt % max(1, total_files // 10) == 0 or done_cnt == total_files:
                pct = (done_cnt / total_files) * 100
                print(f"  Progresso: {done_cnt}/{total_files} ({pct:.0f}%) concluído...", flush=True)

    if failed:
        return False
    print(f"  [OK] Todos os módulos compilados para x86-64 em {time.time() - t_comp:.1f}s!")

    # 4. Link final com lld-link
    print("\n[FASE 3/3] Vinculando biblioteca nativa final (lasgame.dll)...")
    t_link = time.time()

    # Copiar lasrecomp.dll.a para obj_dir como lasrecomp.lib para evitar problemas com caminhos
    local_lib = os.path.join(obj_dir, "lasrecomp.lib")
    if os.path.exists(import_lib) and not os.path.exists(local_lib):
        shutil.copy2(import_lib, local_lib)

    objs_rsp = os.path.join(obj_dir, "objs.rsp")
    with open(objs_rsp, "w", encoding="ascii") as f:
        for o in obj_files:
            f.write(f'"{o}"\n')
        if os.path.exists(local_lib):
            f.write(f'"{local_lib}"\n')

    link_rsp = os.path.join(zig_rt, "link.rsp")
    link_cmd = f'"{zig_exe}" lld-link "@{link_rsp}" "-LIBPATH:{zig_rt}" "-OUT:{out_dll}" "@{objs_rsp}"'
    ok = run_cmd(link_cmd, "Link do lasgame.dll")
    if not ok:
        return False

    dll_size = os.path.getsize(out_dll) / (1024 * 1024)
    print(f"  [SUCESSO] lasgame.dll gerado com sucesso! Tamanho: {dll_size:.2f} MB ({time.time() - t_link:.1f}s)")

    # 5. Gerar ID do build
    build_id = "pla_v100_7fcad279"
    with open(out_id, "w", encoding="ascii") as f:
        f.write(f"{build_id}\n")
    print(f"  [OK] Build ID registrado em lasgame.dll.id: {build_id}")

    total_time = time.time() - t_start
    print("\n==========================================================")
    print(f" RECOMPILAÇÃO CONCLUÍDA EM {total_time:.1f}s!")
    print(f" DLL Nativa: {out_dll}")
    print("==========================================================\n")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pokémon Legends: Arceus Recomp Build System")
    parser.add_argument("--test", action="store_true", help="Modo de teste rápido com limite de funções")
    parser.add_argument("--limit", type=int, default=50, help="Número de funções por módulo no modo teste")
    parser.add_argument("--jobs", type=int, default=None, help="Número de threads simultâneas para compilação")
    parser.add_argument("--force-gen", action="store_true", help="Forçar nova tradução lasgen de todos os módulos")
    args = parser.parse_args()

    success = build_recomp(test_mode=args.test, limit=args.limit, max_workers=args.jobs, force_gen=args.force_gen)
    sys.exit(0 if success else 1)
