import sys
import os

def ensure_venv():
    """
    Checks if the script is running in a virtual environment.
    If not, it re-executes the script with the venv's Python interpreter.
    """
    # Path to the virtual environment
    venv_dir = os.path.join(os.path.dirname(__file__), ".venv")
    
    # Determine the path to the Python executable within the venv
    if sys.platform == "win32":
        venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
    else: # macOS, Linux, etc.
        venv_python = os.path.join(venv_dir, "bin", "python")

    # Check if we are already running in the venv
    # sys.prefix is the venv path, sys.base_prefix is the global Python path
    if sys.prefix == os.path.abspath(venv_dir):
        return

    # If the venv Python exists, re-run the script with it
    if os.path.exists(venv_python):
        print("Not in a virtual environment. Re-launching with .venv/bin/python...")
        os.execv(venv_python, [venv_python, __file__] + sys.argv[1:])

if __name__ == "__main__":
    ensure_venv()
    from app import socketio, app # This import is now safe
    print("\nTeleprompter server running at http://localhost:5000/\n")
    socketio.run(app, host="0.0.0.0", port=5000)
