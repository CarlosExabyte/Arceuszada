import os
import re

targets = [
    "C:/Users/Carlos/Desktop/ZA Recomp/build/generated/main_1229.c",
    "C:/Users/Carlos/Desktop/ZA Recomp/build/generated/main_1230.c",
    "C:/Users/Carlos/Desktop/ZA Recomp/build/generated/main_1231.c",
]

explicit_funcs = {
    "f_7102a62880", "f_7102a6f754", "f_7102a81bf0", "f_7102a837d4", "f_7102a838a0"
}

func_header_re = re.compile(r"void\s+(f_71[0-9a-fA-F]+)\s*\(\s*Cpu\s*\*c\s*\)\s*\{")

for target in targets:
    if not os.path.exists(target):
        continue
    with open(target, "r", encoding="utf-8", errors="ignore") as fp:
        content = fp.read()
    
    matches = list(func_header_re.finditer(content))
    print(f"Scanning {os.path.basename(target)}: {len(matches)} functions found")
    
    # We will build the new content
    new_pieces = []
    last_pos = 0
    patched_count = 0
    
    for i, m in enumerate(matches):
        fn_name = m.group(1)
        fn_addr = int(fn_name.replace("f_", ""), 16)
        start = m.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(content)
        body = content[start:end]
        
        # Check if function should be patched:
        has_tail_dispatch = "rt_dispatch(c)" in body
        has_l_dispatch = "L_dispatch:" in body
        is_explicit = fn_name in explicit_funcs
        
        if has_tail_dispatch or has_l_dispatch or is_explicit:
            # Find all internal labels
            labels = re.findall(r"L_(71[0-9a-fA-F]+):;", body)
            int_labels = sorted(list(set(l for l in labels if int(l, 16) > fn_addr)), key=lambda x: int(x, 16))
            
            if int_labels:
                lo_hex = f"{fn_addr:x}"
                hi_hex = int_labels[-1]
                
                # Check if already patched at top
                top_pattern = f"if (c->pc >= 0x{lo_hex}ull"
                if top_pattern not in body:
                    # Construct entry switch
                    cases = []
                    for lbl in int_labels:
                        cases.append(f"        case 0x{lbl}ull: c->pc = 0; goto L_{lbl};")
                    cases_str = "\n".join(cases)
                    
                    entry_switch = (
                        f"    if (c->pc >= 0x{lo_hex}ull && c->pc <= 0x{hi_hex}ull && c->pc != 0x{lo_hex}ull) {{\n"
                        f"        switch (c->pc) {{\n"
                        f"{cases_str}\n"
                        f"        default: break;\n"
                        f"        }}\n"
                        f"    }}\n"
                        f"    c->pc = 0;\n"
                        f"    FN_ENTER(0x{lo_hex}ull);"
                    )
                    
                    # Replace FN_ENTER(0x...ull); with entry_switch
                    old_fn_enter = f"    FN_ENTER(0x{lo_hex}ull);"
                    if old_fn_enter in body:
                        body = body.replace(old_fn_enter, entry_switch, 1)
                        patched_count += 1
                        
                        # Also in L_dispatch, ensure c->pc = 0 is reset before goto
                        # e.g. case 0x71...ull: goto L_71...; -> case 0x71...ull: c->pc = 0; goto L_71...;
                        body = re.sub(r"(case\s+0x71[0-9a-fA-F]+ull:\s*)goto\s+(L_71[0-9a-fA-F]+;)", r"\1c->pc = 0; goto \2", body)
        
        new_pieces.append(content[last_pos:start])
        new_pieces.append(body)
        last_pos = end
        
    new_pieces.append(content[last_pos:])
    new_content = "".join(new_pieces)
    
    with open(target, "w", encoding="utf-8") as fp:
        fp.write(new_content)
    
    print(f"  -> Patched {patched_count} functions in {os.path.basename(target)}")
