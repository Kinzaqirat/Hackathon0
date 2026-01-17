import shutil
from pathlib import Path
import os

VAULT_ROOT = Path(r"e:\obsidian\AI_Employee_Vault")
task_id = "EMAIL_19bcc39d7b99f069.md"

needs_action_path = VAULT_ROOT / "Needs_Action"
done_path = VAULT_ROOT / "Done"
done_path.mkdir(parents=True, exist_ok=True)

src_main = needs_action_path / task_id
print(f"Checking {src_main}...")

if not src_main.exists():
    print(f"Error: {task_id} not found")
else:
    try:
        base_name = src_main.stem
        print(f"Base name: {base_name}")
        related_files = list(needs_action_path.glob(f"{base_name}.*"))
        print(f"Related files: {related_files}")
        
        for file_path in related_files:
            dest = done_path / file_path.name
            print(f"Moving {file_path} to {dest}...")
            if dest.exists():
                print("Destination exists, removing...")
                if dest.is_dir(): shutil.rmtree(dest)
                else: dest.unlink()
            
            shutil.move(str(file_path), str(dest))
        print("Success!")
    except Exception as e:
        print(f"Failure: {e}")
