import subprocess, re

print(f"{str.ljust(chr(27)+chr(91)+chr(49)+chr(109)+chr(78)+chr(79)+chr(68)+chr(69)+chr(27)+chr(91)+chr(48)+chr(109), 20)} {str.ljust(chr(84)+chr(89)+chr(80)+chr(69), 15)} {str.ljust(chr(84)+chr(79)+chr(84), 10)} {str.ljust(chr(85)+chr(83)+chr(69)+chr(68), 10)} {str.ljust(chr(27)+chr(91)+chr(49)+chr(59)+chr(51)+chr(55)+chr(109)+chr(70)+chr(82)+chr(69)+chr(69)+chr(27)+chr(91)+chr(48)+chr(109), 15)}")
print("-" * 65)

try:
    # 1. Get list of nodes in gpu_cuda partition
    nodes_raw = subprocess.check_output(["sinfo", "-p", "gpu_cuda", "-h", "-o", "%N"]).decode("utf-8").strip()
    # Replace ranges like bun[001-003] is hard to parse in one go for scontrol sometimes, 
    # but scontrol usually handles comma lists. Let"s assume standard names or let scontrol expand.
    
    # 2. Get details for these nodes
    # We pass the raw node list string directly to scontrol
    raw = subprocess.check_output(f"scontrol show node {nodes_raw}", shell=True).decode("utf-8")
    
    found_any = False
    
    # scontrol separates nodes with double newlines
    for block in raw.split("\n\n"):
        if "NodeName=" not in block: continue
        
        name = re.search(r"NodeName=(\S+)", block).group(1)
        
        # Extract GPU Config (Gres=gpu:TYPE:COUNT)
        # Bunya strings look like: Gres=gpu:l40s:3
        cfg = re.search(r"Gres=gpu:([^:]+):(\d+)", block)
        if not cfg: continue
        
        gpu_type = cfg.group(1)
        total_gpus = int(cfg.group(2))
        
        # Extract Allocation (AllocTRES=...gres/gpu=COUNT)
        # Note: AllocTRES tracks total GPUs used regardless of type
        used_gpus = 0
        alloc = re.search(r"AllocTRES=.*?gres/gpu=(\d+)", block)
        if alloc:
            used_gpus = int(alloc.group(1))
            
        free = total_gpus - used_gpus
        
        if free > 0:
            found_any = True
            color_free = f"\033[1;32m{free}\033[0m" # Green
            print(f"{name:<15} {gpu_type:<10} {total_gpus:<10} {used_gpus:<10} {color_free:<15}")

    if not found_any:
        print("\n\033[1;31m[RESULT] All GPUs in gpu_cuda are currently FULL.\033[0m")
        print("Your job is queued because there is physically no space right now.")

except Exception as e:
    print(f"Error parsing nodes: {e}")
