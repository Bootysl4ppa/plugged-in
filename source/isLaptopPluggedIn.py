import psutil
import subprocess
import time
import threading
import pystray
from pystray import MenuItem as item
from PIL import Image
import winreg
import logging
import win32api
import win32con
import os

# Get the current script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
NIRCMD_PATH = os.path.join(script_dir, "nircmd.exe")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

high_performance_enabled = False

def is_plugged_in():
    battery = psutil.sensors_battery()
    if battery is None:
        return None
    return battery.power_plugged

def get_display_settings():
    try:
        devmode = win32api.EnumDisplaySettings(None, win32con.ENUM_CURRENT_SETTINGS)
        current_resolution = (devmode.PelsWidth, devmode.PelsHeight)
        current_bpp = devmode.BitsPerPel
        logging.info(f"Current resolution: {current_resolution[0]}x{current_resolution[1]}, {current_bpp} bpp")
        return current_resolution, current_bpp
    except Exception as e:
        logging.error(f"Failed to get current display settings: {e}")
        return None, None

def get_highest_refresh_rate():
    try:
        highest_rate = 0
        i = 0
        while True:
            try:
                mode = win32api.EnumDisplaySettings(None, i)
                if mode.DisplayFrequency > highest_rate:
                    highest_rate = mode.DisplayFrequency
                i += 1
            except:
                break
        logging.info(f"Highest available refresh rate detected: {highest_rate}Hz")
        return highest_rate
    except Exception as e:
        logging.error(f"Failed to detect refresh rate: {e}")
        return None

def set_refresh_rate(resolution, bpp, refresh_rate):
    try:
        # Use NirCmd to change the refresh rate, keeping the resolution and bpp constant
        subprocess.run(
            [NIRCMD_PATH, "setdisplay", str(resolution[0]), str(resolution[1]), str(bpp), str(refresh_rate)],
            check=True
        )
        logging.info(f"Refresh rate set to {refresh_rate}Hz for resolution {resolution[0]}x{resolution[1]} and {bpp} bpp")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to set refresh rate: {e}")

def get_power_plan_guid(plan_name):
    try:
        result = subprocess.run(["powercfg", "-list"], capture_output=True, text=True, check=True)
        lines = result.stdout.splitlines()
        for line in lines:
            if plan_name.lower() in line.lower():
                guid = line.split(':')[1].strip().split(' ')[0].strip()
                logging.info(f"Found power plan {plan_name}: {guid}")
                return guid
        logging.error(f"Power plan {plan_name} not found.")
        return None
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to list power plans: {e}")
        return None

def set_power_plan(plan_guid):
    try:
        subprocess.run(
            ["powercfg", "/setactive", plan_guid],
            check=True
        )
        logging.info(f"Power plan set to {plan_guid}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to set power plan: {e}")

def enable_battery_saver(enable):
    try:
        if enable:
            subprocess.run(
                ["powercfg", "/setdcvalueindex", "SCHEME_CURRENT", "SUB_ENERGYSAVER", "ESBATTTHRESHOLD", "100"],
                check=True
            )
            subprocess.run(
                ["powercfg", "/setactive", "SCHEME_CURRENT"],
                check=True
            )
            logging.info("Battery Saver enabled")
        else:
            subprocess.run(
                ["powercfg", "/setdcvalueindex", "SCHEME_CURRENT", "SUB_ENERGYSAVER", "ESBATTTHRESHOLD", "0"],
                check=True
            )
            subprocess.run(
                ["powercfg", "/setactive", "SCHEME_CURRENT"],
                check=True
            )
            logging.info("Battery Saver disabled")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to set Battery Saver: {e}")

def set_power_mode(mode):
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Power\PowerSettings\54533251-82be-4824-96c1-47b60b740d00\bc5038f7-23e0-4960-96da-33abaf5935ec", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "DCSettingIndex", 0, winreg.REG_DWORD, mode)
        winreg.SetValueEx(key, "ACSettingIndex", 0, winreg.REG_DWORD, mode)
        winreg.CloseKey(key)
        logging.info(f"Power mode set to {mode}")
    except Exception as e:
        logging.error(f"Failed to set power mode: {e}")

def on_high_performance(icon, item):
    global high_performance_enabled
    high_performance_enabled = not high_performance_enabled
    
    if high_performance_enabled:
        logging.info("High Performance mode enabled.")
        set_power_plan(POWER_PLAN_HIGH_PERFORMANCE)
        enable_battery_saver(False)
        set_power_mode(best_performance)
    else:
        logging.info("High Performance mode disabled.")
        if not is_plugged_in():
            set_power_plan(POWER_PLAN_ECO)
            enable_battery_saver(True)
            set_power_mode(best_power_efficiency)

def on_exit(icon, item):
    icon.stop()
    # Add any cleanup code here if needed

def create_image():
    try:
        # Load the custom icon image
        image = Image.open("pluggedIn.png")
        return image
    except FileNotFoundError:
        logging.error("Icon image file not found.")
        return None

def setup_tray_icon():
    icon = pystray.Icon("Laptop Monitor")
    image = create_image()
    if image is not None:
        icon.icon = image
        icon.menu = pystray.Menu(
            item('High Performance', on_high_performance, checked=lambda item: high_performance_enabled),
            item('Exit', on_exit)
        )
        icon.run()
    else:
        logging.error("Failed to set up tray icon.")

def main():
    refresh_rate_not_plugged_in = 60  # Refresh rate when not plugged in

    # Detect highest available refresh rate
    highest_refresh_rate = get_highest_refresh_rate()
    if highest_refresh_rate is None:
        logging.error("Could not determine the highest refresh rate. Using default 60Hz.")
        highest_refresh_rate = 60

    refresh_rate_plugged_in = highest_refresh_rate  # Use detected highest refresh rate when plugged in

    # Get current resolution and bpp
    current_resolution, current_bpp = get_display_settings()
    if current_resolution is None or current_bpp is None:
        logging.error("Could not determine the current resolution and bpp. Using default values 2560x1600 and 32 bpp.")
        current_resolution = (2560, 1600)
        current_bpp = 32

    # Get power plan GUIDs
    global POWER_PLAN_HIGH_PERFORMANCE
    global POWER_PLAN_ECO
    POWER_PLAN_HIGH_PERFORMANCE = get_power_plan_guid("High performance")
    POWER_PLAN_ECO = get_power_plan_guid("Power saver")

    if POWER_PLAN_HIGH_PERFORMANCE is None or POWER_PLAN_ECO is None:
        logging.error("Required power plans not found. Exiting.")
        return

    # Power mode values
    global best_performance
    global best_power_efficiency
    best_performance = 3
    best_power_efficiency = 1

    last_status = None
    last_refresh_rate = None
    last_power_plan = None
    last_battery_saver = None
    last_power_mode = None

    while True:
        plugged_in = is_plugged_in()
        
        if plugged_in is None:
            logging.warning("Could not retrieve battery information.")
        else:
            if plugged_in:  # Laptop is plugged in
                if last_status != 'plugged':
                    logging.info("Laptop is plugged in.")
                    if last_refresh_rate != refresh_rate_plugged_in:
                        set_refresh_rate(current_resolution, current_bpp, refresh_rate_plugged_in)
                        last_refresh_rate = refresh_rate_plugged_in
                    if not high_performance_enabled:
                        if last_power_plan != POWER_PLAN_HIGH_PERFORMANCE:
                            set_power_plan(POWER_PLAN_HIGH_PERFORMANCE)
                            last_power_plan = POWER_PLAN_HIGH_PERFORMANCE
                        if last_battery_saver != False:
                            enable_battery_saver(False)
                            last_battery_saver = False
                        if last_power_mode != best_performance:
                            set_power_mode(best_performance)
                            last_power_mode = best_performance
                    last_status = 'plugged'
            else:  # Laptop is not plugged in
                if last_status != 'unplugged':
                    logging.info("Laptop is not plugged in.")
                    if last_refresh_rate != refresh_rate_not_plugged_in:
                        set_refresh_rate(current_resolution, current_bpp, refresh_rate_not_plugged_in)
                        last_refresh_rate = refresh_rate_not_plugged_in
                    if not high_performance_enabled:
                        if last_power_plan != POWER_PLAN_ECO:
                            set_power_plan(POWER_PLAN_ECO)
                            last_power_plan = POWER_PLAN_ECO
                        if last_battery_saver != True:
                            enable_battery_saver(True)
                            last_battery_saver = True
                        if last_power_mode != best_power_efficiency:
                            set_power_mode(best_power_efficiency)
                            last_power_mode = best_power_efficiency
                    last_status = 'unplugged'

        time.sleep(10)

if __name__ == "__main__":
    threading.Thread(target=main, daemon=True).start()
    setup_tray_icon()
