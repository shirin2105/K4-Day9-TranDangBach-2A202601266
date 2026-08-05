import json
import os
from pathlib import Path
from src.config import INPUT_DIR, OUTPUT_DIR
from src.supervisor import SupervisorAgent

def main():
    print("[+] Initializing Multi-Agent Dispute Resolution Pipeline...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    supervisor = SupervisorAgent()
    input_files = sorted(list(INPUT_DIR.glob("EC_*.json")))
    
    print(f"[+] Found {len(input_files)} cases to process in input/")
    
    success_count = 0
    for input_file in input_files:
        try:
            output_data = supervisor.process_case(input_file)
            output_file = OUTPUT_DIR / input_file.name
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
                
            success_count += 1
            print(f"  [ok] Processed {input_file.name} -> output/{output_file.name}")
        except Exception as e:
            print(f"  [err] Error processing {input_file.name}: {str(e)}")
            
    print(f"\n[+] Pipeline execution completed! Successfully generated {success_count}/{len(input_files)} cases in output/")


if __name__ == "__main__":
    main()
