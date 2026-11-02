#!/usr/bin/env python3
"""
Global Jump Table Resolution for PokeZ-ARecomp (Pokemon Legends: Arceus)
Scans all 4 NSOs (main, subsdk0, subsdk1, sdk), extracts all valid jump table targets
(including hoisted ADRP jump tables up to 2,000 instructions back), inserts missing
labels L_<target>:; at exact instruction offsets, and injects universal top-of-function
entry switches into containing functions with exact global next_fn_addr bounds.
"""

import os
import sys
import glob
import re
import bisect
import struct

tools_dir = os.path.dirname(os.path.abspath(__file__))
if tools_dir not in sys.path:
    sys.path.insert(0, tools_dir)
import nso

EXECD_DIR = r"D:\Games\Pokemon Legends - Arceus\legends of arceus roomfs e exefs\exefs"
GEN_DIR = r"C:\Users\Carlos\Desktop\ZA Recomp\build\generated"

MODULES = [
    ("main",    0x7100000000),
    ("subsdk0", 0x7104800000),
    ("subsdk1", 0x7105000000),
    ("sdk",     0x7106000000),
]

def extract_all_jump_table_targets():
    all_targets = set()
    print("Extracting jump table targets across all 4 NSOs (with hoisted ADRP recovery)...")
    for mod_name, base_addr in MODULES:
        path = os.path.join(EXECD_DIR, mod_name)
        if not os.path.exists(path):
            print(f"  [WARN] {path} not found!")
            continue
        n = nso.Nso(path)
        text_off, text_sz = n.text
        mod_count = 0
        jt_count = 0
        for pc in range(text_off, text_off + text_sz, 4):
            w = n.u32(pc)
            # Check for BR Xn
            if (w & 0xfffffc1f) == 0xd61f0000:
                rn = (w >> 5) & 0x1f
                prev = n.u32(pc - 4)
                # Check for ADD shifted right before BR: ADD Xd, Xn, Xm, LSL #shift (or SXTW/UXTW)
                if ((prev & 0xff200000) == 0x8b000000 or (prev & 0xff200000) == 0x8b200000) and (prev & 0x1f) == rn:
                    window = [n.u32(pc - i*4) for i in range(40, -1, -1)]
                    cmp_limit = None
                    for i in range(len(window)-2, -1, -1):
                        w_c = window[i]
                        if (w_c & 0x7f80001f) == 0x7100001f:
                            cmp_limit = (w_c >> 10) & 0xfff
                            break
                    if cmp_limit is None or cmp_limit > 1024:
                        continue
                    
                    table_addr = None
                    block_base = None
                    elem_size = None
                    signed = True
                    table_reg = None
                    
                    # Search close window (last 10 instructions before BR) for ADR and LDR
                    for back in range(1, 12):
                        ipc = pc - back * 4
                        if ipc < text_off:
                            break
                        w_i = n.u32(ipc)
                        # ADR
                        if block_base is None and (w_i & 0x9f000000) == 0x10000000:
                            immlo = (w_i >> 29) & 3
                            immhi = (w_i >> 5) & 0x7ffff
                            imm = ((immhi << 2) | immlo)
                            if imm & (1 << 20): imm -= (1 << 21)
                            block_base = ipc + imm
                        # Element load (LDRB, LDRSB, LDRH, LDRSH, LDRSW)
                        if elem_size is None:
                            if (w_i & 0xffee0000) == 0x78680000 or (w_i & 0xffa00000) == 0x78800000:
                                elem_size = 2; signed = True; table_reg = (w_i >> 5) & 0x1f
                            elif (w_i & 0xffe00000) == 0x79400000 or (w_i & 0xffe00000) == 0x78400000:
                                elem_size = 2; signed = False; table_reg = (w_i >> 5) & 0x1f
                            elif (w_i & 0xffe00000) == 0xb8800000 or (w_i & 0xffa00000) == 0xb8800000:
                                elem_size = 4; signed = True; table_reg = (w_i >> 5) & 0x1f
                            elif (w_i & 0xffe00000) == 0x38400000 or (w_i & 0xffe00000) == 0x39400000:
                                elem_size = 1; signed = False; table_reg = (w_i >> 5) & 0x1f
                            elif (w_i & 0xffa00000) == 0x38800000:
                                elem_size = 1; signed = True; table_reg = (w_i >> 5) & 0x1f
                    
                    # Search backwards up to 2,000 instructions for ADRP + ADD (or ADR) setting table_reg
                    if table_reg is not None:
                        add_off = None
                        for back in range(2, 2000):
                            ipc = pc - back * 4
                            if ipc < text_off:
                                break
                            w_i = n.u32(ipc)
                            # ADD Xd, Xn, #imm12
                            if add_off is None and (w_i & 0xff800000) == 0x91000000 and (w_i & 0x1f) == table_reg:
                                add_off = (w_i >> 10) & 0xfff
                                table_reg = (w_i >> 5) & 0x1f
                            elif (w_i & 0x9f000000) == 0x90000000 and (w_i & 0x1f) == table_reg:
                                immlo = (w_i >> 29) & 3
                                immhi = (w_i >> 5) & 0x7ffff
                                imm = ((immhi << 2) | immlo)
                                if imm & (1 << 20): imm -= (1 << 21)
                                page = (ipc & ~0xfff) + (imm << 12)
                                if add_off is not None:
                                    table_addr = page + add_off
                                break
                            elif (w_i & 0x9f000000) == 0x10000000 and (w_i & 0x1f) == table_reg and ipc < pc - 16:
                                immlo = (w_i >> 29) & 3
                                immhi = (w_i >> 5) & 0x7ffff
                                imm = ((immhi << 2) | immlo)
                                if imm & (1 << 20): imm -= (1 << 21)
                                table_addr = ipc + imm + (add_off or 0)
                                break
                    
                    if table_addr and block_base and elem_size:
                        jt_count += 1
                        for idx in range(cmp_limit + 1):
                            pos = table_addr + idx * elem_size
                            if pos + elem_size > len(n.image):
                                break
                            if elem_size == 1:
                                off = struct.unpack_from('<B' if not signed else '<b', n.image, pos)[0]
                            elif elem_size == 2:
                                off = struct.unpack_from('<h' if signed else '<H', n.image, pos)[0]
                            elif elem_size == 4:
                                off = struct.unpack_from('<i' if signed else '<I', n.image, pos)[0]
                            target = block_base + (off << 2)
                            if text_off <= target < text_off + text_sz and target % 4 == 0:
                                all_targets.add(base_addr + target)
                                mod_count += 1
        print(f"  {mod_name}: {jt_count} jump tables, {mod_count} targets extracted")
    print(f"Total unique jump table targets in .text: {len(all_targets)}")
    return all_targets

def main():
    targets = extract_all_jump_table_targets()
    
    files = sorted(glob.glob(os.path.join(GEN_DIR, "*.c")))
    print(f"Scanning {len(files)} generated C files...")
    
    fn_re = re.compile(r"void\s+(f_71[0-9a-fA-F]+)\s*\(\s*Cpu\s*\*c\s*\)\s*\{")
    
    fn_to_file = {}
    fn_list = []
    
    for f in files:
        with open(f, "r", encoding="utf-8", errors="ignore") as fp:
            content = fp.read()
        for m in fn_re.finditer(content):
            fn_name = m.group(1)
            fn_addr = int(fn_name[2:], 16)
            fn_to_file[fn_addr] = f
            fn_list.append(fn_addr)
    
    fn_list.sort()
    fn_next_map = {}
    for idx, addr in enumerate(fn_list):
        if idx + 1 < len(fn_list) and (fn_list[idx+1] - addr) < 0x100000:
            fn_next_map[addr] = fn_list[idx+1]
        else:
            fn_next_map[addr] = addr + 0x10000
    print(f"Total functions indexed: {len(fn_list)}")
    
    # Map targets to containing functions
    fn_targets_map = {}
    affected_files = set()
    
    for t in targets:
        idx = bisect.bisect_right(fn_list, t) - 1
        if 0 <= idx < len(fn_list):
            fn_addr = fn_list[idx]
            next_addr = fn_next_map[fn_addr]
            if fn_addr <= t < next_addr:
                fn_targets_map.setdefault(fn_addr, set()).add(t)
                affected_files.add(fn_to_file[fn_addr])
    
    # Also include any file that already has an injected entry switch or L_dispatch
    for f in files:
        if f not in affected_files:
            with open(f, "r", encoding="utf-8", errors="ignore") as fp:
                txt = fp.read()
            if "L_dispatch:" in txt or "rt_unmapped_block(" in txt:
                affected_files.add(f)
    
    print(f"Files to process: {len(affected_files)}")
    
    total_labels_inserted = 0
    total_funcs_switched = 0
    modified_files_count = 0
    
    lbl_re = re.compile(r"L_(71[0-9a-fA-F]+):;")
    
    for file_path in sorted(affected_files):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as fp:
            content = fp.read()
        
        matches = list(fn_re.finditer(content))
        if not matches:
            continue
            
        file_modified = False
        new_pieces = []
        last_pos = 0
        
        for i, m in enumerate(matches):
            fn_name = m.group(1)
            fn_addr = int(fn_name[2:], 16)
            next_fn_addr = fn_next_map[fn_addr]
            
            start = m.start()
            end = matches[i+1].start() if i + 1 < len(matches) else len(content)
            body = content[start:end]
            
            targets_in_fn = fn_targets_map.get(fn_addr, set())
            has_ldispatch = "L_dispatch:" in body
            has_rtdispatch = "rt_dispatch(c)" in body
            has_existing_sw = "rt_unmapped_block(" in body
            
            if targets_in_fn or has_ldispatch or has_rtdispatch or has_existing_sw:
                existing_labels = set(int(x, 16) for x in lbl_re.findall(body))
                missing_targets = [t for t in targets_in_fn if t not in existing_labels and fn_addr < t < next_fn_addr]
                
                # Insert missing labels if any
                if missing_targets:
                    lines = body.splitlines(keepends=True)
                    stmt_indices = []
                    in_switch = False
                    for line_idx, line in enumerate(lines):
                        s = line.strip()
                        if s.startswith("if (__builtin_expect(c->pc != 0"):
                            in_switch = True
                            continue
                        if in_switch:
                            if s.startswith("FN_ENTER("):
                                in_switch = False
                            continue
                        if not s or s.startswith("void ") or s.startswith("FN_ENTER") or (s.startswith("L_") and s.endswith(":;")):
                            continue
                        stmt_indices.append(line_idx)
                    
                    for t in sorted(missing_targets, reverse=True):
                        inst_idx = (t - fn_addr) // 4
                        if inst_idx < len(stmt_indices):
                            target_line_idx = stmt_indices[inst_idx]
                            lines.insert(target_line_idx, f"L_{t:x}:;\n")
                            existing_labels.add(t)
                            total_labels_inserted += 1
                            file_modified = True
                    body = "".join(lines)
                
                # Check if we should inject/update the top entry switch
                int_labels = sorted(list(set(l for l in existing_labels if fn_addr < l < next_fn_addr)))
                if int_labels and (targets_in_fn or has_ldispatch or has_existing_sw):
                    lo_hex = f"{fn_addr:x}"
                    hi_hex = f"{next_fn_addr:x}"
                    cases = [f"        case 0x{lbl:x}ull: c->pc = 0; goto L_{lbl:x};" for lbl in int_labels]
                    cases_str = "\n".join(cases)
                    
                    entry_switch = (
                        f"    if (__builtin_expect(c->pc != 0, 0)) {{\n"
                        f"        switch (c->pc) {{\n"
                        f"        case 0x{lo_hex}ull: c->pc = 0; break;\n"
                        f"{cases_str}\n"
                        f"        default:\n"
                        f"            if (c->pc < 0x{lo_hex}ull || c->pc >= 0x{hi_hex}ull) {{ c->pc = 0; break; }}\n"
                        f"            rt_unmapped_block(c, 0x{lo_hex}ull, c->pc);\n"
                        f"            return;\n"
                        f"        }}\n"
                        f"    }}\n"
                        f"    c->pc = 0;\n"
                        f"    FN_ENTER(0x{lo_hex}ull);"
                    )
                    
                    new_sw = re.search(r"    if \(__builtin_expect\(c->pc != 0, 0\)\) \{.*?FN_ENTER\(0x[0-9a-fA-F]+ull\);", body, re.DOTALL)
                    old_sw = re.search(r"    if \(c->pc >= 0x[0-9a-fA-F]+ull.*?FN_ENTER\(0x[0-9a-fA-F]+ull\);", body, re.DOTALL)
                    
                    if new_sw:
                        if body[new_sw.start():new_sw.end()] != entry_switch:
                            body = body[:new_sw.start()] + entry_switch + body[new_sw.end():]
                            total_funcs_switched += 1
                            file_modified = True
                    elif old_sw:
                        body = body[:old_sw.start()] + entry_switch + body[old_sw.end():]
                        total_funcs_switched += 1
                        file_modified = True
                    else:
                        old_enter = f"    FN_ENTER(0x{lo_hex}ull);"
                        if old_enter in body:
                            body = body.replace(old_enter, entry_switch, 1)
                            total_funcs_switched += 1
                            file_modified = True
                    
                    if has_ldispatch:
                        new_body = re.sub(r"(case\s+0x71[0-9a-fA-F]+ull:\s*)goto\s+(L_71[0-9a-fA-F]+;)", r"\1c->pc = 0; goto \2", body)
                        if new_body != body:
                            body = new_body
                            file_modified = True
            
            new_pieces.append(content[last_pos:start])
            new_pieces.append(body)
            last_pos = end
        
        new_pieces.append(content[last_pos:])
        new_content = "".join(new_pieces)
        
        if file_modified and new_content != content:
            with open(file_path, "w", encoding="utf-8") as fp:
                fp.write(new_content)
            modified_files_count += 1
    
    print(f"\n[SUCESSO] Patch global concluido!")
    print(f"  Rotulos L_<target>:; inseridos: {total_labels_inserted}")
    print(f"  Funcoes atualizadas com entry switch: {total_funcs_switched}")
    print(f"  Arquivos C modificados: {modified_files_count}")

if __name__ == "__main__":
    main()
