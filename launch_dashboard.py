import subprocess
import os
from pathlib import Path

def run_dashboard():
    vault_root = Path(__file__).parent.resolve()
    api_script = vault_root / "web_dashboard" / "api.py"
    
    print("🚀 Starting Digital FTE Web Dashboard...")
    print(f"📂 Vault Root: {vault_root}")
    print("🌐 Dashboard will be available at: http://localhost:8000")
    
    try:
        # Start the FastAPI server
        subprocess.run(["uv", "run", "python", str(api_script)], check=True)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped.")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")

if __name__ == "__main__":
    run_dashboard()
