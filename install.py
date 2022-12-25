import os
import shutil
from modules.scripts import basedir
import launch

if not launch.is_installed("colorama"):
        launch.run_pip("install colorama")
from colorama import just_fix_windows_console, Fore, Style
just_fix_windows_console()

update_flag = "preset_manager_update_check"

additional_config_source = "additional_components.json"
additional_config_target = "additional_configs.json"
presets_config_source = "preset_configuration.json"
presets_config_target = "presets.json"

#source_file = "preset_utils.py"
#target_filename = "zzz.preset_utils.py"
#target_path = os.path.join(basedir(), "scripts", target_filename)


extensions_path = os.path.join(basedir(), "extensions")
if os.path.exists(extensions_path):
    for extfiles in os.listdir(extensions_path):
        file_path = os.path.join(extensions_path, extfiles)
        if os.path.isdir(file_path):
            ext_scripts_path = os.path.join(file_path, "scripts")
            if os.path.exists(ext_scripts_path):
                path_to_update_flag = os.path.join(ext_scripts_path, update_flag)
                if os.path.exists(path_to_update_flag):
                    print(Fore.CYAN + "Thank you for using:" + Fore.GREEN + "https://github.com/Gerschel/sd_web_ui_preset_utils/")
                    print(Fore.RED +"""
______                   _    ___  ___                                  
| ___ \                 | |   |  \/  |                                  
| |_/ / __ ___  ___  ___| |_  | .  . | __ _ _ __   __ _  __ _  ___ _ __ 
|  __/ '__/ _ \/ __|/ _ \ __| | |\/| |/ _` | '_ \ / _` |/ _` |/ _ \ '__|
| |  | | |  __/\__ \  __/ |_  | |  | | (_| | | | | (_| | (_| |  __/ |   
\_|  |_|  \___||___/\___|\__| \_|  |_/\__,_|_| |_|\__,_|\__, |\___|_|   
                                                         __/ |          
                                                        |___/           
""")
                    print(Fore.YELLOW + "By: Gerschel Payne")
                    print(Style.RESET_ALL + "Preset Manager: Checking for pre-existing configuration files.")

                    source_path = os.path.join(file_path, additional_config_source)
                    target_path = os.path.join(file_path, additional_config_target)
                    if not os.path.exists(target_path):
                        shutil.move(source_path, target_path)
                        print(f"Created: {additional_config_target}")
                    else:
                        print(f"Not writing {additional_config_target}: config exists already")
                    
                    source_path = os.path.join(file_path, presets_config_source)
                    target_path = os.path.join(file_path, presets_config_target)
                    if not os.path.exists(target_path):
                        shutil.move(source_path, target_path)
                        print(f"Created: {presets_config_target}")
                    else:
                        print(f"Not writing {presets_config_target}: config exists already")
                    
                    
                    os.remove(path_to_update_flag)
                    break



