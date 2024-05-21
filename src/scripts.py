import subprocess, sys, os

# An example script path = C:\\Users\\USER\\Desktop\\my_script.ps1
# Also adding the execution policy in order to avoid Security exception error

def _run_elevated_powershell_script(script_path_full, args):
    """
    Runs the specified PowerShell script with elevated privileges and args.

    Args:
        script_path_full: The full path to the PowerShell script file.
        args: A string containing the args to pass to the script.
    """

    command = (
        f'powershell -Command "Start-Process powershell '
        f'-Verb RunAs -ArgumentList \'-NoProfile -ExecutionPolicy Bypass -File \"{script_path_full}\" {args}\'"'
    )

    subprocess.call(command, shell=True)

def _get_full_path(relative_path):
    """
    Expects this python script to be ran from the root project directory, and a windows-style path(?)
    """

    return os.path.join(os.path.dirname(__file__), relative_path)

def run_all_reg_files():
    reg_file_path_full = _get_full_path("..\\data")
    script_path_full = _get_full_path("..\\script\\run_all_reg_files.ps1")

    args = f"-reg_dir_path {reg_file_path_full}"

    _run_elevated_powershell_script(script_path_full, args)

def create_hive():
    hive_export_path_full = _get_full_path("..\\data\\HIVE.DAT")

    script_path_full = _get_full_path("..\\script\\create_hive.ps1")
    args = f"-export_path {hive_export_path_full}"

    _run_elevated_powershell_script(script_path_full, args)

def load_hive():
    hive_filepath = _get_full_path("..\\data\\HIVE.DAT")

    script_path = _get_full_path("..\\script\\load_hive.ps1")
    args = f"-hive_filepath {hive_filepath}"

    _run_elevated_powershell_script(script_path, args)

def unload_hive():
    script_path = _get_full_path("..\\script\\unload_hive.ps1")
    args = f""

    _run_elevated_powershell_script(script_path, args)

if __name__ == "__main__":
    create_hive()
    #run_all_reg_files()
    load_hive()
    unload_hive()