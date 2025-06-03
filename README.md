```markdown
# **CPU Temperature Monitor**

A Python script to monitor CPU temperatures, providing interactive console updates, JSON output, or a concise short-form summary.  
**GitHub Repository:** [github.com/tugapse/cpu-temp](https://github.com/tugapse/cpu-temp)

## **Features**

*   **Interactive Display:** Real-time, flicker-free (on compatible terminals) updates of CPU and core temperatures in a two-column layout.
*   **Overall and Core Temperatures:** Separates the aggregate "Overall" CPU temperature from individual core temperatures.
*   **Sequential Core Labeling:** Cores are automatically sorted and labeled sequentially (e.g., Core 1, Core 2, ...).
*   **Color-Coded Temperatures:** Temperatures are displayed in green (normal), yellow (warm), or red (hot) based on configurable thresholds.
*   **JSON Output:** Export current temperature data in a structured JSON format for scripting or integration.
*   **Short Output:** Get a quick, single-line summary of current temperatures.

## **Installation**

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/tugapse/cpu-temp.git
    cd cpu-temp
    ```

2.  Install dependencies:
    This script primarily relies on psutil for system information.
    ```bash
    pip install psutil
    ```

    *Note: The script uses standard Python libraries and ANSI escape codes for console coloring and cursor movement. Modern terminals (Linux, macOS, Windows Terminal, VS Code terminal) typically support these natively. If you encounter issues on older Windows cmd.exe, you might need to install colorama (pip install colorama), though it's not strictly required by this version of the script.*

## **How to Use**

The script offers different modes of operation via command-line arguments.

### **1\. Interactive Real-time Monitoring (Default)**

Run the script without any arguments to get a continuously updating display of your CPU temperatures. This mode attempts to be flicker-free by moving the cursor and overwriting output.
```bash
python cpu_temp_monitor.py
```

### **2\. JSON Output**

Use the `--json` flag to get a single snapshot of the CPU temperature data in JSON format. The script will print the JSON and then exit. This is useful for scripting or integrating with other tools.
```bash
python cpu_temp_monitor.py --json
```

**Example JSON Output:**
```json
{
  "timestamp": "2025-06-03T12:55:25.123456",
  "overall_cpu_temp": {
    "label": "Overall",
    "current": 51.0,
    "high": 100.0,
    "critical": 100.0
  },
  "cores_temp": [
    {
      "label": "Core 1",
      "original_label": "Core 0",
      "current": 46.0,
      "high": 100.0,
      "critical": 100.0
    },
    {
      "label": "Core 2",
      "original_label": "Core 4",
      "current": 45.0,
      "high": 100.0,
      "critical": 100.0
    }
    // ... more cores
  ]
}
```

### **3\. Short Summary Output**

Use the `--short` or `-s` flag to get a concise, single-line summary of the current overall and core temperatures. The script will print this line and then exit.
```bash
python cpu_temp_monitor.py --short
```
```bash
# or
python cpu_temp_monitor.py -s
```

**Example Short Output:**
```
OV: 51.0°C | C1: 46.0°C | C2: 45.0°C | C3: 47.0°C | ...
```

## **Troubleshooting**

*   **Flickering in Interactive Mode:** If you experience flickering, ensure your terminal emulator supports ANSI escape codes. Modern terminals like Windows Terminal, VS Code's integrated terminal, or any Linux/macOS terminal should work well. If not, consider using a library like rich (though not included by default in this version) for more robust terminal rendering.
*   **"No CPU temperature data available"**: This might mean psutil cannot find the appropriate sensor driver on your system (coretemp, k10temp, or acpitz). The error message will list available sensor keys, which might help in debugging.
*   **Permission Denied:** On some Linux systems, accessing sensor data might require appropriate permissions or running with sudo.

## **Contributing**

Feel free to open issues or pull requests on the [GitHub repository](https://github.com/tugapse/cpu-temp) if you have suggestions, bug reports, or improvements!
```