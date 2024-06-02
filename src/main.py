import os
import re

import chardet
from tqdm import tqdm

import scripts

# TODO: put _get_full_path outside of scripts.py
INF_DIRPATH = scripts._get_full_path("..\input")
DATA_DIRPATH = scripts._get_full_path("..\data")
REGISTRY_KEY_DEFAULT = "HKEY_USERS\\INF_REG_TO_HIVE"

# TODO: make registrypath.join

def main():
    print("Creating empty hive...")
    scripts.create_hive()

    print("Generating .reg files...")
    generate_reg_files()

    print("Loading empty hive...")
    scripts.load_hive()

    print("Running all .reg files (populating hive)...")
    scripts.run_all_reg_files()

    print(f"Done! Go to {REGISTRY_KEY_DEFAULT} to see the result!")

def generate_reg_files():
    # TODO: better progress/iteration bar (currently tracks all files, not just .inf)
    for dirpath, _, filenames in tqdm(os.walk(INF_DIRPATH)):
        for filename in filenames:
            if filename.lower().endswith(".inf"):
                inf_filename = filename
                inf_filepath = os.path.join(dirpath, inf_filename)
                inf_addreg_entries = extract_inf_addreg_entries(inf_filepath)

                if inf_addreg_entries is None:
                    continue

                reg_content = "Windows Registry Editor Version 5.00\n\n" # latest version, for Windows 2000 and later.
                for device, lines in inf_addreg_entries.items():
                    reg_lines = inf_to_reg(lines, f"{REGISTRY_KEY_DEFAULT}\\{inf_filename[:-4]}\\{device}")
                    reg_content += f"\n{reg_lines}"

                reg_filename = inf_filename[:-4] + ".reg"
                reg_filepath = os.path.join(DATA_DIRPATH, reg_filename)

                with open(reg_filepath, "w") as f:
                    f.write(reg_content)

def extract_inf_addreg_entries(inf_filepath):
    # TODO: make this dict setup cleaner
    device_addreg_sections = {}  # Dictionary to store registry sections by device
    device_addreg_entries = {} # Dictionary to store registry lines by device
    inf_section_pattern = re.compile(r'\[([^\]]+)\]')

    with open(inf_filepath, 'rb') as f:
        bytes = f.read()
        encoding = chardet.detect(bytes)['encoding']

    with open(inf_filepath, 'r', errors="replace", encoding=encoding) as f:
        curr_device = None
        for i, line in enumerate(f):
            # Match section headers (e.g., [RTL8169.ndi.NT])
            match = inf_section_pattern.match(line)
            if match:
                curr_device = match.group(1)
                device_addreg_sections[curr_device] = []
            # Match AddReg directives within sections
            elif re.match(r'^addreg\s*=', line, re.IGNORECASE):
                addreg_sections = [x.strip() for x in line.split("=")[1].split(",")]
                device_addreg_sections[curr_device].extend(addreg_sections)

        # remove "devices" with no registry sections
        device_addreg_sections = {k:v for k, v in device_addreg_sections.items() if v}
        curr_device = None
        curr_addreg_section = None
        f.seek(0)

        for i, line in enumerate(f):
            match = inf_section_pattern.match(line)
            if match:
                matched_devices = 0
                # consider creating inverse dict (reg_section: device), and then re-inverting it again in the end?
                for device, sections in device_addreg_sections.items():
                    if match.group(1) in sections:
                        curr_addreg_section = match.group(1)
                        device_addreg_entries[device] = []
                        matched_devices += 1
                if matched_devices == 0:
                    curr_addreg_section = None
            elif curr_addreg_section:
                for device, sections in device_addreg_sections.items():
                    if curr_addreg_section in sections:
                        device_addreg_entries[device].append(line)

    return device_addreg_entries

def inf_to_reg(inf_addreg_entries, custom_key="HKEY_LOCAL_MACHINE\\SOFTWARE\\MyCustomLocation"):
    reg_lines = []

    for inf_addreg_line in inf_addreg_entries:
        inf_addreg_entry_match = re.match(r'(\w+),([^,]*),([^,]*),([^,]*),(.+)', inf_addreg_line)
        if inf_addreg_entry_match:
            root_key, subkey, value_name, value_type, value_data = inf_addreg_entry_match.groups()
            reg_lines.append(f"[{custom_key}\\{root_key}\\{subkey}]")
            reg_lines.append(f'    "{value_name if value_name else ""}"="{value_data}"')  

    return "\n".join(reg_lines)

if __name__ == "__main__":
    main()