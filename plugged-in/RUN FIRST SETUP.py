import os
import subprocess
import urllib.request
import zipfile
import getpass
import sys

def install_packages():
    try:
        print("Installing required packages...")
        # Install winshell
        subprocess.check_call([sys.executable, "-m", "pip", "install", "winshell"])
        print("Installed winshell successfully.")
        
        # Install additional packages
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil", "screen_brightness_control", "pystray", "pillow", "pywin32"])
        print("Installed additional packages successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install packages: {e}")
        sys.exit(1)

def download_nircmd():
    try:
        print("Downloading nircmd...")
        # URL for nircmd.zip
        nircmd_url = "https://www.nirsoft.net/utils/nircmd.zip"
        nircmd_zip_path = os.path.join(os.getcwd(), "nircmd.zip")
        nircmd_exe_path = os.path.join(os.getcwd(), "nircmd.exe")
        
        # Download nircmd.zip
        urllib.request.urlretrieve(nircmd_url, nircmd_zip_path)
        
        # Extract nircmd.exe from the zip file
        with zipfile.ZipFile(nircmd_zip_path, 'r') as zip_ref:
            zip_ref.extract("nircmd.exe", os.getcwd())
        
        # Clean up the zip file
        os.remove(nircmd_zip_path)
        
        print(f"nircmd.exe downloaded and placed in {os.getcwd()} successfully.")
    except Exception as e:
        print(f"Failed to download or extract nircmd: {e}")
        sys.exit(1)

def create_shortcut():
    try:
        import winshell
        
        print("Creating shortcut...")
        # Get the current username
        username = getpass.getuser()
        
        # Define the path to the executable and the shortcut
        exe_path = os.path.join(os.getcwd(), 'isLaptopPluggedIn.exe')
        shortcut_path = os.path.join(
            'C:\\Users', username, 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'isLaptopPluggedIn.lnk'
        )
        
        # Create the shortcut
        with winshell.shortcut(shortcut_path) as shortcut:
            shortcut.path = exe_path
            shortcut.description = "Shortcut to isLaptopPluggedIn.exe"
            shortcut.working_directory = os.getcwd()
        
        print(f"Shortcut created at {shortcut_path} successfully.")
        
        # Ask the user if they want to add the program to startup
        add_to_startup = input("Do you want to add plugged in to startup? (yes/no): ")
        if add_to_startup.lower() == "yes":
            startup_folder = os.path.join('C:\\Users', username, 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
            startup_shortcut_path = os.path.join(startup_folder, 'isLaptopPluggedIn.lnk')
            
            # Copy the shortcut to the startup folder
            shutil.copy2(shortcut_path, startup_shortcut_path)
            print("Added to startup successfully.")
        else:
            print("Not adding to startup.")
    except Exception as e:
        print(f"Failed to create shortcut or add to startup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_packages()
    download_nircmd()
    create_shortcut()
