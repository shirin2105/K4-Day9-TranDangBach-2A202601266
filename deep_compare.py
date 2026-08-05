import zipfile, json
from pathlib import Path

ref_data = {}
with zipfile.ZipFile(r'C:\Users\trand\Downloads\Others\output.zip', 'r') as zipf:
    for name in zipf.namelist():
        if name.endswith('.json'):
            fname = Path(name).name
            ref_data[fname] = json.loads(zipf.read(name).decode('utf-8'))

my_dir = Path('output')

for fname in sorted(ref_data.keys()):
    ref = ref_data[fname]
    my_file = my_dir / fname
    with open(my_file, 'r', encoding='utf-8') as f:
        mine = json.load(f)

    # Deep key comparison
    def compare_dicts(d1, d2, path=""):
        if type(d1) != type(d2):
            print(f"TYPE MISMATCH at {path}: {type(d1)} vs {type(d2)}")
            return
        if isinstance(d1, dict):
            for k in d1:
                if k not in d2:
                    print(f"MISSING KEY in mine at {path}.{k}")
                else:
                    compare_dicts(d1[k], d2[k], f"{path}.{k}")
            for k in d2:
                if k not in d1:
                    print(f"EXTRA KEY in mine at {path}.{k}")
        elif isinstance(d1, list):
            if len(d1) != len(d2):
                print(f"LENGTH MISMATCH at {path}: ref={len(d1)} vs mine={len(d2)}")
            for idx, (i1, i2) in enumerate(zip(d1, d2)):
                compare_dicts(i1, i2, f"{path}[{idx}]")
        else:
            if d1 != d2:
                print(f"VALUE DIFF at {path}: ref={repr(d1)} vs mine={repr(d2)}")

    print(f"--- Comparing {fname} ---")
    compare_dicts(ref, mine, fname)
