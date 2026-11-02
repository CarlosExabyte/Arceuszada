import re
import glob

targets = ["main_1229.c", "main_1230.c", "main_1231.c"]
base_dir = "C:/Users/Carlos/Desktop/ZA Recomp/build/generated/"

for target in targets:
    path = base_dir + target
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Find all function definitions: void f_71XXXX(Cpu *c) {
    func_pattern = re.compile(r"void\s+(f_71[0-9a-fA-F]+)\(Cpu\s*\*c\)\s*\{")
    funcs = list(func_pattern.finditer(content))
    print(f"=== {target}: {len(funcs)} functions ===")
    
    for i, m in enumerate(funcs):
        fn_name = m.group(1)
        start_pos = m.start()
        end_pos = funcs[i+1].start() if i + 1 < len(funcs) else len(content)
        fn_body = content[start_pos:end_pos]
        
        # Check if fn_body has rt_dispatch
        if "rt_dispatch(c)" in fn_body:
            # Check for tail dispatch or indirect branch
            tail_matches = re.findall(r"c->pc\s*=\s*(c->x\[\d+\]);\s*__attribute__\(\(musttail\)\)\s*return\s*rt_dispatch\(c\);", fn_body)
            musttail_matches = re.findall(r"__attribute__\(\(musttail\)\)\s*return\s*rt_dispatch\(c\);", fn_body)
            blr_matches = re.findall(r"c->pc\s*=\s*c->x\[\d+\];\s*c->x\[30\]\s*=\s*0x[0-9a-fA-F]+ull;\s*rt_dispatch\(c\);", fn_body)
            labels = re.findall(r"L_(71[0-9a-fA-F]+):;", fn_body)
            
            if tail_matches or (musttail_matches and not blr_matches):
                print(f"Function {fn_name}: {len(labels)} labels, tail_matches: {len(tail_matches)}, musttail: {len(musttail_matches)}, blr: {len(blr_matches)}")
                if len(labels) > 5:
                    print(f"   Sample labels: {labels[:5]} ... {labels[-3:]}")
