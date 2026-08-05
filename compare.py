import zipfile, json
from pathlib import Path

ref_data = {}
with zipfile.ZipFile(r'C:\Users\trand\Downloads\Others\output.zip', 'r') as zipf:
    for name in zipf.namelist():
        if name.endswith('.json'):
            fname = Path(name).name
            ref_data[fname] = json.loads(zipf.read(name).decode('utf-8'))

my_dir = Path('output')
diff_count = 0

for fname in sorted(ref_data.keys()):
    ref = ref_data[fname]
    my_file = my_dir / fname
    with open(my_file, 'r', encoding='utf-8') as f:
        mine = json.load(f)
        
    diffs = []
    if ref['case_assessment']['primary_issue'] != mine['case_assessment']['primary_issue']:
        diffs.append(f"primary_issue: ref={ref['case_assessment']['primary_issue']} vs mine={mine['case_assessment']['primary_issue']}")
        
    if ref['case_assessment']['case_status'] != mine['case_assessment']['case_status']:
        diffs.append(f"case_status: ref={ref['case_assessment']['case_status']} vs mine={mine['case_assessment']['case_status']}")

    if ref['financial_resolution']['recommended_refund_brl'] != mine['financial_resolution']['recommended_refund_brl']:
        diffs.append(f"recommended_refund_brl: ref={ref['financial_resolution']['recommended_refund_brl']} vs mine={mine['financial_resolution']['recommended_refund_brl']}")

    if diffs:
        diff_count += 1
        print(f"=== {fname} Diffs ===")
        for d in diffs:
            print("  -", d)

print(f"\nTotal files with key differences: {diff_count}/50")
