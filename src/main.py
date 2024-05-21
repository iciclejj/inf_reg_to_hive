import os
import re

import chardet

import scripts

INF_DIRPATH_ROOT = "input"
HIVE_PATH_DEFAULT = "data/HIVE.DAT"
REGISTRY_KEY_DEFAULT = "HKEY_USERS\\INF_REG_TO_HIVE"

# TODO: make registrypath.join

def main():
    print("Creating empty hive...")
    scripts.create_hive()

    print("Generating .reg files...")
    _generate_reg_files()

    print("Loading empty hive...")
    scripts.load_hive()

    print("Running all .reg files (populating hive)...")
    scripts.run_all_reg_files()

    print("Done! Go to HKU\\INF_REG_TO_HIVE to see the result!")

def _generate_reg_files():
    for dirpath, _, filenames in os.walk(INF_DIRPATH_ROOT):
        for filename in filenames:
            if filename.lower().endswith(".inf"):
                filepath = os.path.join(dirpath, filename)
                inf_lines = extract_inf_registry_lines(filepath)

                if inf_lines is None:
                    continue

                reg_content = "Windows Registry Editor Version 5.00\n\n"
                for device, lines in inf_lines.items():
                    reg_lines = inf_to_reg(lines, f"{REGISTRY_KEY_DEFAULT}\\{filename.replace(".inf", "")}\\{device}")
                    reg_content += f"\n{reg_lines}"

                filename_reg = filename.lower().replace(".inf", ".reg")
                filepath_reg = os.path.join("data", filename_reg)

                with open(filepath_reg, "w") as f:
                    f.write(reg_content)

def extract_inf_registry_lines(inf_file):
    # TODO: make this dict setup cleaner
    device_reg_sections = {}  # Dictionary to store registry sections by device
    device_reg_lines = {} # Dictionary to store registry lines by device
    # ignoring/replacing errors due to encoding errors.
    #   we will assume crucial sections are all encoded using charmap-compatible encodings
    with open(inf_file, 'rb') as f:
        bytes = f.read()
        encoding = chardet.detect(bytes)['encoding']

    with open(inf_file, 'r', errors="replace", encoding=encoding) as f:
        curr_device = None
        for i, line in enumerate(f):
            # Match section headers (e.g., [RTL8169.ndi.NT])
            match = re.match(r'\[([^\]]+)\]', line)
            if match:
                curr_device = match.group(1)
                device_reg_sections[curr_device] = []
            # Match AddReg directives within sections
            elif curr_device and line.startswith("AddReg"):
                reg_sections = [x.strip() for x in line.split("=")[1].split(",")]
                device_reg_sections[curr_device].extend(reg_sections)

        # remove "devices" with no registry sections
        device_reg_sections = {k:v for k, v in device_reg_sections.items() if v}
        curr_device = None
        curr_reg_section = None
        f.seek(0)

        for i, line in enumerate(f):
            match = re.match(r'\[([^\]]+)\]', line)
            if match:
                matched_devices = 0
                # consider creating inverse dict (reg_section: device), and then re-inverting it again in the end?
                for device, sections in device_reg_sections.items():
                    if match.group(1) in sections:
                        curr_reg_section = match.group(1)
                        device_reg_lines[device] = []
                        matched_devices += 1
                if matched_devices == 0:
                    curr_reg_section = None
            elif curr_reg_section:
                for device, sections in device_reg_sections.items():
                    if curr_reg_section in sections:
                        device_reg_lines[device].append(line)

    return device_reg_lines

def inf_to_reg(inf_lines, custom_key="HKEY_LOCAL_MACHINE\\SOFTWARE\\MyCustomLocation"):
    reg_lines = []

    # TODO: Consider adding root_key to the registry path
    for line in inf_lines:
        match = re.match(r'(\w+),([^,]*),([^,]*),([^,]*),(.+)', line)
        if match:
            root_key, subkey, value_name, value_type, value_data = match.groups()
            reg_lines.append(f"[{custom_key}\\{root_key}\\{subkey}]")
            reg_lines.append(f'    "{value_name if value_name else ""}"="{value_data}"')  

    return "\n".join(reg_lines)

if __name__ == "__main__":
    main()