import os
import sys
import subprocess
import urllib.request
import zipfile
import pathlib
import shutil
from config import load_config

VIRTUAL_ENV_DIR = pathlib.Path("./virtual_env")
DOTNET_INSTALL_DIR = VIRTUAL_ENV_DIR / "dotnet"
TSHOCK_INSTALL_DIR = VIRTUAL_ENV_DIR / "tshock"
TSHOCK_DATA_DIR = pathlib.Path("./tshock")
WORLDS_DIR = pathlib.Path("./worlds")
PLUGINS_DIR = pathlib.Path("./ServerPlugins")

def setup_environment():
    print("--- Setting up environment directories ---")
    VIRTUAL_ENV_DIR.mkdir(exist_ok=True)
    TSHOCK_DATA_DIR.mkdir(exist_ok=True)
    WORLDS_DIR.mkdir(exist_ok=True)
    PLUGINS_DIR.mkdir(exist_ok=True)
    (TSHOCK_DATA_DIR / "logs").mkdir(exist_ok=True)

def install_dotnet():
    dotnet_exe = DOTNET_INSTALL_DIR / "dotnet"
    if dotnet_exe.exists():
        print("--- .NET 6 Runtime already installed ---")
        return

    print("--- .NET 6 Runtime not found, installing... ---")
    install_script_url = "https://dot.net/v1/dotnet-install.sh"
    install_script_path = VIRTUAL_ENV_DIR / "dotnet-install.sh"

    try:
        urllib.request.urlretrieve(install_script_url, install_script_path)
        os.chmod(install_script_path, 0o755)

        subprocess.run(
            [
                str(install_script_path),
                "--runtime", "dotnet",
                "--version", "6.0",
                "--install-dir", str(DOTNET_INSTALL_DIR)
            ],
            check=True
        )
    except Exception as e:
        print(f"Error installing .NET 6 Runtime: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if install_script_path.exists():
            install_script_path.unlink()
    print("--- .NET 6 Runtime installation complete ---")

def install_tshock(config):
    tshock_dll = TSHOCK_INSTALL_DIR / "TShock.Server.dll"
    if tshock_dll.exists():
        print("--- TShock is already installed ---")
        return

    print(f"--- TShock v{config['tshock']['version']} not found, installing... ---")
    download_url = config["tshock"]["download_url"]
    zip_path = VIRTUAL_ENV_DIR / "tshock.zip"

    try:
        print(f"Downloading from {download_url}")
        urllib.request.urlretrieve(download_url, zip_path)

        print(f"Extracting to {TSHOCK_INSTALL_DIR}")
        TSHOCK_INSTALL_DIR.mkdir(exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(TSHOCK_INSTALL_DIR)
    except Exception as e:
        print(f"Error installing TShock: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if zip_path.exists():
            zip_path.unlink()
    print("--- TShock installation complete ---")
    
def build_command(config):
    dotnet_exe = DOTNET_INSTALL_DIR / "dotnet"
    tshock_dll = TSHOCK_INSTALL_DIR / "TShock.Server.dll"
    
    command = [str(dotnet_exe), str(tshock_dll)]
    
    command.extend(["-configpath", str(TSHOCK_DATA_DIR.resolve())])
    command.extend(["-logpath", str((TSHOCK_DATA_DIR / "logs").resolve())])
    command.extend(["-pluginpath", str(PLUGINS_DIR.resolve())])

    for key, param in config["startup_parameters"].items():
        if param.get("enabled", False):
            env_var_name = param.get("env_var")
            value = os.environ.get(env_var_name, param["value"])

            if key == "world" and not value.lower().endswith(('.wld', '.twld')):
                value += ".wld"
            
            command.extend([param["argument"], str(value)])
            
    return command

def run_server(command):
    print("--- Launching TShock Server ---")
    print(f"Executing command: {' '.join(command)}")
    try:
        subprocess.run(command, check=True, cwd=str(TSHOCK_INSTALL_DIR))
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error running TShock server: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    print("--- TShock Python Launcher Initializing ---")
    config = load_config()
    setup_environment()
    install_dotnet()
    install_tshock(config)
    command = build_command(config)
    run_server(command)
    print("--- TShock Server has shut down ---")

if __name__ == "__main__":
    main()
