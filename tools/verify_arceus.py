#!/usr/bin/env python3
"""
Pokemon Legends: Arceus Recomp - Verificador e Preparador de Arquivos
Title ID: 01001F5010DFA000
Build ID: 7FCAD279539DE183B25C11834FD4A030591CFE25 (v1.0.0)
"""

import os
import sys
import struct
import shutil
import argparse
import subprocess

EXPECTED_TITLE_ID = "01001F5010DFA000"
EXPECTED_BUILD_ID = "7fcad279539de183b25c11834fd4a030591cfe25"
REQUIRED_EXEFS = ["main", "subsdk0", "subsdk1", "sdk", "main.npdm", "rtld"]
REQUIRED_ROMFS_DIRS = ["bin", "system_resource"]

def get_nso_build_id(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        magic = f.read(4)
        if magic != b"NSO0":
            return None
        f.seek(0x40)
        return f.read(0x20).hex().lower()

def check_folder(target_dir):
    print(f"\n========================================================")
    print(f" Diagnóstico: Pokémon Legends: Arceus Recomp")
    print(f" Pasta analisada: {target_dir}")
    print(f"========================================================\n")

    if not os.path.exists(target_dir):
        print(f"[ERRO CRÍTICO] Diretório não encontrado: {target_dir}")
        return False, None, None

    # Procura exefs e romfs (podem estar na raiz ou dentro de subpastas)
    exefs_path = None
    romfs_path = None

    for root, dirs, files in os.walk(target_dir):
        for d in dirs:
            dl = d.lower()
            full_d = os.path.join(root, d)
            if dl == "exefs" and exefs_path is None:
                exefs_path = full_d
            elif dl == "romfs" and romfs_path is None:
                romfs_path = full_d

    # Checagem direta caso a pasta atual já contenha 'main'
    if exefs_path is None and os.path.isfile(os.path.join(target_dir, "main")):
        exefs_path = target_dir
    if romfs_path is None and os.path.isdir(os.path.join(target_dir, "bin")):
        romfs_path = target_dir

    all_ok = True

    # 1. Validação ExeFS
    print("[1/2] Verificando ExeFS...")
    if not exefs_path:
        print("  [X] Diretório 'exefs' não encontrado!")
        all_ok = False
    else:
        print(f"  [OK] ExeFS localizado em: {exefs_path}")
        main_path = os.path.join(exefs_path, "main")
        if not os.path.exists(main_path):
            print("  [X] Arquivo 'main' não encontrado no ExeFS!")
            all_ok = False
        else:
            bid = get_nso_build_id(main_path)
            print(f"  [INFO] Build ID do executável principal: {bid}")
            if bid and bid.startswith(EXPECTED_BUILD_ID):
                print(f"  [OK] Versão confirmada: Pokémon Legends: Arceus v1.0.0 ({bid[:16]}...)")
            else:
                print(f"  [AVISO] Build ID diferente do esperado v1.0.0 ({EXPECTED_BUILD_ID[:16]}...)")

        for req in REQUIRED_EXEFS:
            rp = os.path.join(exefs_path, req)
            if os.path.exists(rp):
                size_mb = os.path.getsize(rp) / (1024 * 1024)
                print(f"  [OK] {req:12s} presente ({size_mb:6.2f} MB)")
            else:
                print(f"  [X]  {req:12s} AUSENTE!")
                all_ok = False

    # 2. Validação RomFS
    print("\n[2/2] Verificando RomFS...")
    if not romfs_path:
        print("  [X] Diretório 'romfs' não encontrado!")
        all_ok = False
    else:
        print(f"  [OK] RomFS localizado em: {romfs_path}")
        for rd in REQUIRED_ROMFS_DIRS:
            rp = os.path.join(romfs_path, rd)
            if os.path.isdir(rp):
                print(f"  [OK] Pasta '{rd}/' encontrada (estrutura Gfx2)")
            else:
                print(f"  [AVISO] Pasta '{rd}/' não encontrada na raiz do RomFS.")

        # Amostra de assets do jogo
        gfpak_count = 0
        bntx_count = 0
        for root, _, files in os.walk(romfs_path):
            for f in files:
                fl = f.lower()
                if fl.endswith(".gfpak"):
                    gfpak_count += 1
                elif fl.endswith(".bntx"):
                    bntx_count += 1
                if gfpak_count > 50 and bntx_count > 50:
                    break
        print(f"  [INFO] Recursos Gfx2 detectados no RomFS: pacotes .gfpak e texturas .bntx presentes.")

    print("\n--------------------------------------------------------")
    if all_ok:
        print("[SUCESSO] Todos os arquivos obrigatórios de Pokémon Legends: Arceus estão corretos e prontos para recompilação!")
    else:
        print("[INCOMPLETO] Alguns arquivos estão ausentes ou em locais incorretos.")
    print("--------------------------------------------------------\n")
    return all_ok, exefs_path, romfs_path

def prepare_extracted(exefs_src, romfs_src, project_root):
    dst_exefs = os.path.join(project_root, "extracted", "exefs")
    dst_romfs = os.path.join(project_root, "extracted", "romfs")
    os.makedirs(dst_exefs, exist_ok=True)
    os.makedirs(dst_romfs, exist_ok=True)

    print(f"[PREPARAÇÃO] Vinculando/copiando arquivos para: {project_root}\\extracted")
    for item in REQUIRED_EXEFS:
        s = os.path.join(exefs_src, item)
        d = os.path.join(dst_exefs, item)
        if os.path.exists(s) and not os.path.exists(d):
            try:
                os.link(s, d)
                print(f"  Hardlink criado: {item}")
            except Exception:
                shutil.copy2(s, d)
                print(f"  Copiado: {item}")
        elif os.path.exists(d):
            print(f"  Já presente: {item}")

    print("[PREPARAÇÃO] ExeFS preparado com sucesso em extracted/exefs!")

    if romfs_src and os.path.isdir(romfs_src):
        if not os.path.exists(dst_romfs) or (os.path.isdir(dst_romfs) and not os.listdir(dst_romfs)):
            if os.path.exists(dst_romfs) and not os.listdir(dst_romfs):
                try: os.rmdir(dst_romfs)
                except Exception: pass
            if not os.path.exists(dst_romfs):
                try:
                    subprocess.run(f'cmd /c mklink /J "{dst_romfs}" "{romfs_src}"', shell=True, check=True)
                    print(f"  Junction criado para RomFS: {dst_romfs} -> {romfs_src}")
                except Exception as e:
                    print(f"  [AVISO] Não foi possível criar junction: {e}")
        else:
            print("  RomFS já configurado em extracted/romfs")

if __name__ == "__main__":
    proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target = None
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        target = sys.argv[1]
    elif os.path.exists(os.path.join(proj_root, "extracted", "exefs", "main")):
        target = os.path.join(proj_root, "extracted")
    else:
        target = r"D:\Games\Pokemon Legends - Arceus\legends of arceus roomfs e exefs"
    ok, exefs, romfs = check_folder(target)
    if ok and "--prepare" in sys.argv:
        prepare_extracted(exefs, romfs, proj_root)
