import glob
import re

files = sorted(glob.glob("C:/Users/Carlos/Desktop/ZA Recomp/build/generated/main_*.c"))
print(f"Scanning {len(files)} files...")

func_pattern = re.compile(r"void\s+(f_71[0-9a-fA-F]+)\(Cpu\s*\*c\)\s*\{")

total_jt_funcs = 0
jt_funcs_info = []

for f in files:
    with open(f, "r", encoding="utf-8", errors="ignore") as fp:
        content = fp.read()
    
    matches = list(func_pattern.finditer(content))
    for i, m in enumerate(matches):
        fn_name = m.group(1)
        fn_addr = int(fn_name.replace("f_", ""), 16)
        start = m.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(content)
        body = content[start:end]
        
        # Check if there is a tail dispatch:
        # e.g., c->pc = ...; __attribute__((musttail)) return rt_dispatch(c);
        # OR __attribute__((musttail)) return rt_dispatch(c);
        if "rt_dispatch(c)" in body:
            # Look for lines where c->pc is set and rt_dispatch is called without setting c->x[30]
            # Pattern 1: c->pc = c->x[...]; __attribute__((musttail)) return rt_dispatch(c);
            # Pattern 2: __attribute__((musttail)) return rt_dispatch(c);
            has_tail_dispatch = bool(re.search(r"__attribute__\(\(musttail\)\)\s*return\s*rt_dispatch\(c\);", body))
            
            # Pattern 3: c->pc = c->x[...]; rt_dispatch(c); where c->x[30] is NOT set on the same line or line before
            has_br = bool(re.search(r"c->pc\s*=\s*c->x\[\d+\];\s*rt_dispatch\(c\);", body))
            
            if has_tail_dispatch or has_br:
                labels = re.findall(r"L_(71[0-9a-fA-F]+):;", body)
                # Filter labels to only those strictly inside this function (i.e. addr >= fn_addr)
                int_labels = [l for l in labels if int(l, 16) > fn_addr]
                if int_labels:
                    total_jt_funcs += 1
                    jt_funcs_info.append((f, fn_name, fn_addr, int_labels))

print(f"Found {total_jt_funcs} functions with internal jump tables/labels across all main files!")
for f, fn_name, fn_addr, labels in jt_funcs_info[:15]:
    print(f"  {fn_name} in {f.split('/')[-1]}: {len(labels)} internal labels")
