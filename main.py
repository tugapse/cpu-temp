import psutil
import time
import os
import re
import sys
import argparse
import json
from datetime import datetime

# Define ANSI escape codes directly
ANSI_RESET = "\x1b[0m"
ANSI_RED = "\x1b[31m"
ANSI_GREEN = "\x1b[32m"
ANSI_YELLOW = "\x1b[33m"
ANSI_BLUE = "\x1b[34m"
ANSI_CYAN = "\x1b[36m"
ANSI_WHITE = "\x1b[37m"

def clear_console():
    """
    Moves the cursor to the top-left of the console and clears the screen from that point.
    This prevents flickering compared to os.system('clear/cls').
    Uses raw ANSI escape codes.
    """
    sys.stdout.write("\x1b[H\x1b[J")
    sys.stdout.flush()

def get_temp_color(temperature):
    """Returns an ANSI color code based on the temperature value."""
    if temperature < 60:
        return ANSI_GREEN
    elif temperature < 80:
        return ANSI_YELLOW
    else:
        return ANSI_RED

def get_sort_key(sensor):
    """Helper function to extract a sortable key from the sensor label (for cores only)."""
    label = sensor.label
    match = re.search(r'(\d+)', label)
    if match:
        return int(match.group(1))
    return 9999

def get_cpu_data_structured():
    """
    Fetches and structures CPU temperature data into a Python dictionary.
    This data can then be used for display or JSON output.
    """
    data = {
        "timestamp": datetime.now().isoformat(),
        "overall_cpu_temp": None,
        "cores_temp": []
    }

    try:
        raw_temps = psutil.sensors_temperatures()
        all_cpu_sensors = raw_temps.get('coretemp') or \
                          raw_temps.get('k10temp') or \
                          raw_temps.get('acpitz')

        if not all_cpu_sensors:
            data["error"] = "No CPU temperature data found. This script might not support your system's sensor names."
            data["available_sensor_keys"] = list(raw_temps.keys())
            return data

        package_sensor = None
        core_sensors = []

        for sensor in all_cpu_sensors:
            if "package id" in sensor.label.lower():
                package_sensor = sensor
            else:
                core_sensors.append(sensor)

        if package_sensor:
            data["overall_cpu_temp"] = {
                "label": "Overall",
                "current": package_sensor.current,
                "high": package_sensor.high,
                "critical": package_sensor.critical
            }

        core_sensors.sort(key=get_sort_key)

        core_counter = 1
        for sensor in core_sensors:
            data["cores_temp"].append({
                "label": f"Core {core_counter}",
                "original_label": sensor.label,
                "current": sensor.current,
                "high": sensor.high,
                "critical": sensor.critical
            })
            core_counter += 1
    except Exception as e:
        data["error"] = f"Error during data collection: {e}"
        data["available_sensor_keys"] = list(raw_temps.keys()) if 'raw_temps' in locals() else []
    
    return data


def display_cpu_temperatures(cpu_data):
    """
    Displays CPU temperature data in a formatted console output.
    Takes structured data from get_cpu_data_structured().
    """
    sys.stdout.write(f"{ANSI_CYAN}--- CPU Temperature Monitor ---{ANSI_RESET}\n")

    # --- Display Overall CPU Information (Header/Separate Line) ---
    if cpu_data.get("overall_cpu_temp"):
        package_info = cpu_data["overall_cpu_temp"]
        package_color = get_temp_color(package_info["current"])
        current_pkg_str = f"{package_info['current']:.1f}°C"
        high_pkg_str = f"{package_info['high']:.1f}°C"
        critical_pkg_str = f"{package_info['critical']:.1f}°C"
        
        PKG_LABEL_WIDTH = 12
        PKG_VALUE_WIDTH = 7

        sys.stdout.write("-" * 55 + "\n")
        sys.stdout.write(f"{ANSI_BLUE}{'Overall':<{PKG_LABEL_WIDTH}}{'Current':<{PKG_VALUE_WIDTH+1}}{'High':<{PKG_VALUE_WIDTH+1}}{'Critical':<{PKG_VALUE_WIDTH+1}}{ANSI_RESET}\n")
        sys.stdout.write("-" * 55 + "\n")
        sys.stdout.write(f"{'':<{PKG_LABEL_WIDTH}}"
                         f"{package_color}{current_pkg_str:<{PKG_VALUE_WIDTH+1}}{ANSI_RESET}"
                         f"{high_pkg_str:<{PKG_VALUE_WIDTH+1}}{ANSI_RESET}"
                         f"{critical_pkg_str:<{PKG_VALUE_WIDTH+1}}{ANSI_RESET}\n")
        sys.stdout.write("-" * 55 + "\n")
    elif "error" in cpu_data: # If a general error occurred during data collection
        sys.stdout.write(f"{ANSI_YELLOW}{cpu_data['error']}{ANSI_RESET}\n")
        if "available_sensor_keys" in cpu_data:
            sys.stdout.write(f"{ANSI_YELLOW}Available sensor keys: {', '.join(cpu_data['available_sensor_keys'])}{ANSI_RESET}\n")
        sys.stdout.write("-" * 55 + "\n")
        sys.stdout.flush()
        return
    else: # No overall data, but not a full error state (e.g., system only has cores)
        sys.stdout.write(f"{ANSI_YELLOW}No 'Overall' (Package) temperature data found.{ANSI_RESET}\n")
        sys.stdout.write("-" * 55 + "\n")


    # --- Display Individual Cores (Two Columns) ---
    core_sensors_data = cpu_data.get("cores_temp", [])
    if not core_sensors_data:
        sys.stdout.write(f"{ANSI_YELLOW}No individual core temperature data available.{ANSI_RESET}\n")
        sys.stdout.write("-" * 55 + "\n")
        sys.stdout.flush()
        return

    LABEL_WIDTH = 12
    TEMP_VALUE_WIDTH = 7
    
    LINE_LENGTH = (LABEL_WIDTH + 3 * (TEMP_VALUE_WIDTH + 1)) * 2 + 5

    sys.stdout.write(f"{ANSI_CYAN}--- Individual Cores ---{ANSI_RESET}\n")
    sys.stdout.write("-" * LINE_LENGTH + "\n")

    col_header = f"{ANSI_BLUE}{'Core':<{LABEL_WIDTH}}{'Cur':<{TEMP_VALUE_WIDTH+1}}{'Hi':<{TEMP_VALUE_WIDTH+1}}{'Crit':<{TEMP_VALUE_WIDTH+1}}{ANSI_RESET}"
    sys.stdout.write(f"{col_header}     {col_header}\n")

    sys.stdout.write("-" * LINE_LENGTH + "\n")

    num_cores = len(core_sensors_data)
    mid_point = (num_cores + 1) // 2

    col1_cores = core_sensors_data[:mid_point]
    col2_cores = core_sensors_data[mid_point:]

    for i in range(mid_point):
        # Column 1
        sensor1_info = col1_cores[i]
        display_label1 = sensor1_info["label"]
        
        color1 = get_temp_color(sensor1_info["current"])
        current_temp_str1 = f"{sensor1_info['current']:.1f}°C"
        high_temp_str1 = f"{sensor1_info['high']:.1f}°C"
        critical_temp_str1 = f"{sensor1_info['critical']:.1f}°C"

        line1 = (f"{ANSI_WHITE}{display_label1:<{LABEL_WIDTH}}{ANSI_RESET}"
                 f"{color1}{current_temp_str1:<{TEMP_VALUE_WIDTH+1}}{ANSI_RESET}"
                 f"{high_temp_str1:<{TEMP_VALUE_WIDTH+1}}{ANSI_RESET}"
                 f"{critical_temp_str1:<{TEMP_VALUE_WIDTH+1}}{ANSI_RESET}")

        # Column 2
        line2 = ""
        if i < len(col2_cores):
            sensor2_info = col2_cores[i]
            display_label2 = sensor2_info["label"]
            
            color2 = get_temp_color(sensor2_info["current"])
            current_temp_str2 = f"{sensor2_info['current']:.1f}°C"
            high_temp_str2 = f"{sensor2_info['high']:.1f}°C"
            critical_temp_str2 = f"{sensor2_info['critical']:.1f}°C"

            line2 = (f"{ANSI_WHITE}{display_label2:<{LABEL_WIDTH}}{ANSI_RESET}"
                     f"{color2}{current_temp_str2:<{TEMP_VALUE_WIDTH+1}}{ANSI_RESET}"
                     f"{high_temp_str2:<{TEMP_VALUE_WIDTH+1}}{ANSI_RESET}"
                     f"{critical_temp_str2:<{TEMP_VALUE_WIDTH+1}}{ANSI_RESET}")

        sys.stdout.write(f"{line1}     {line2}\n")

    sys.stdout.write("-" * LINE_LENGTH + "\n")
    sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser(description="Monitor CPU temperatures.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output temperature data in JSON format and exit."
    )
    parser.add_argument(
        "--short", "-s",
        action="store_true",
        help="Output a short, single-line version of current temperatures and exit."
    )
    args = parser.parse_args()

    # Handle mutually exclusive arguments
    if args.json and args.short:
        sys.stderr.write("Error: --json and --short arguments are mutually exclusive.\n")
        sys.exit(1)

    # --- Mode selection ---
    if args.json or args.short:
        # For --json or --short, fetch data once
        cpu_data = get_cpu_data_structured()

        if "error" in cpu_data:
            sys.stderr.write(f"{ANSI_RED}Error fetching CPU data: {cpu_data['error']}{ANSI_RESET}\n")
            if "available_sensor_keys" in cpu_data:
                sys.stderr.write(f"{ANSI_YELLOW}Available sensor keys: {', '.join(cpu_data['available_sensor_keys'])}{ANSI_RESET}\n")
            sys.exit(1)

        if args.json:
            try:
                json_output = json.dumps(cpu_data, indent=2)
                sys.stdout.write(json_output + "\n")
                sys.stdout.flush()
            except Exception as e:
                sys.stderr.write(f"Error generating JSON output: {e}\n")
                sys.exit(1)
            sys.exit(0) # Exit after JSON output
        elif args.short:
            short_output_parts = []

            # Overall CPU temperature
            if cpu_data.get("overall_cpu_temp"):
                short_output_parts.append(f"OV: {cpu_data['overall_cpu_temp']['current']:.1f}°C")
            else:
                short_output_parts.append("OV: N/A")

            # Individual core temperatures
            for core in cpu_data.get("cores_temp", []):
                short_output_parts.append(f"{core['label'].replace('Core ', 'C')}: {core['current']:.1f}°C")

            sys.stdout.write(" | ".join(short_output_parts) + "\n")
            sys.stdout.flush()
            sys.exit(0) # Exit after short output
    else:
        # Default interactive monitoring mode
        while True:
            clear_console()
            try:
                cpu_data_live = get_cpu_data_structured()
                display_cpu_temperatures(cpu_data_live)
            except Exception as e:
                sys.stdout.write(f"{ANSI_RED}An error occurred: {e}{ANSI_RESET}\n")
                sys.stdout.flush()
            time.sleep(2)

if __name__ == "__main__":
    main()