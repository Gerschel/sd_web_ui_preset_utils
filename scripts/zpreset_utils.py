import gradio as gr
import modules.sd_samplers
import modules.scripts as scripts
from modules import shared
import json
import os
import shutil
from pprint import pprint
from modules.ui import gr_show
from collections import namedtuple
from pathlib import Path

#  *********     versioning     *****
repo = None
version_map = {
    'https://github.com/vladmandic/automatic':"vlads",
    None: "a1111"
    }
#Test for a1111 or vlads, vlad had the courtesy to set a variable
if hasattr(shared, "url"):
    repo = version_map[getattr(shared, "url")]
else:
    repo = "a1111"

try:
    import launch

    if not launch.is_installed("colorama"):
            launch.run_pip("install colorama")
except:
    pass

try:
    from colorama import just_fix_windows_console, Fore, Style
    just_fix_windows_console()
except:
    pass

update_flag = "preset_manager_update_check"

additional_config_source = "additional_components.json"
additional_config_target = "additional_configs.json"
presets_config_source = "preset_configuration.json"
presets_config_target = "presets.json"

file_path = scripts.basedir() # file_path is basedir
scripts_path = os.path.join(file_path, "scripts")
path_to_update_flag = os.path.join(scripts_path, update_flag)
is_update_available = False
if os.path.exists(path_to_update_flag):
    is_update_available = True
    try:
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
    except NameError:
        print( "Thank you for using: https://github.com/Gerschel/sd_web_ui_preset_utils/")
        print("""
______                   _    ___  ___                                  
| ___ \                 | |   |  \/  |                                  
| |_/ / __ ___  ___  ___| |_  | .  . | __ _ _ __   __ _  __ _  ___ _ __ 
|  __/ '__/ _ \/ __|/ _ \ __| | |\/| |/ _` | '_ \ / _` |/ _` |/ _ \ '__|
| |  | | |  __/\__ \  __/ |_  | |  | | (_| | | | | (_| | (_| |  __/ |   
\_|  |_|  \___||___/\___|\__| \_|  |_/\__,_|_| |_|\__,_|\__, |\___|_|   
                                                         __/ |          
                                                        |___/           
""")
        print("By: Gerschel Payne")
        print("Preset Manager: Checking for pre-existing configuration files.")


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



class PresetManager(scripts.Script):

    BASEDIR = scripts.basedir()

    def update_component_name(self, preset, oldval, newval):
        if preset.get(oldval) is not None:
            preset[newval] = preset.pop(oldval)

    def update_config(self):
        """This is a as per need method that will change per need"""
        component_remap = {
            "Highres. fix": "Hires. fix",
            "Firstpass width": "Upscaler",
            "Firstpass height": "Upscale by",
            "Sampling Steps": "Sampling steps",
            "Hires. steps": "Hires steps"
            }
        
        if repo == "vlads":
            component_remap.update({
                "Hires. fix" : "Hires fix"
            })

        
        config = self.get_config(self.settings_file)
        for preset in config.values():
            for old_val, new_val in component_remap.items():
                self.update_component_name(preset, old_val, new_val)
                    
        #PresetManager.all_presets = config
        self.save_config(self.settings_file, config)


    def __init__(self, *args, **kwargs):
        
        self.compinfo = namedtuple("CompInfo", ["component", "label", "elem_id", "kwargs"])

        #self.settings_file = "preset_configuration.json"
        self.settings_file = "presets.json"
        #self.additional_settings_file = "additional_components.json"
        self.additional_settings_file = "additional_configs.json"


        self.additional_components_for_presets = self.get_config(self.additional_settings_file) #additionalComponents
        self.available_components = [
            "Prompt", #! must create filter for hr prompt and neg prompt using elem_id in after component 5/28/23
            "Negative prompt",
            "Sampling steps",
            "Sampling method",
            "Width",
            "Height",
            "Restore faces",
            "Tiling",
            "Hires. fix" if repo != "vlads" else "Hires fix",#NewNew Vlads #!update config needs a version check
            "Highres. fix",#old
            "Upscaler",#new
            "Upscale by",#new
            "Hires. steps",#NewOld,
            "Hires steps",#NewNew
            "Resize width to",#New
            "Resize height to",#New
            "Hires sampling method",#Newest 5/27/23
            "Seed",
            "Extra",
            "Variation seed",
            "Variation strength",
            "Resize seed from width",
            "Resize seed from height",
            "Firstpass width",#old now is upscaler
            "Firstpass height",#old now is upscale by
            "Denoising strength",
            "Batch count",
            "Batch size",
            "CFG Scale",
            "Image CFG Scale",
            "Script",
            "Input directory",
            "Output directory",
            "Inpaint batch mask directory (required for inpaint batch processing only)",
            "Resize mode",
            "Scale",
            "Mask blur",
            "Mask transparency",
            "Mask mode",
            "Masked content",
            "Inpaint area",
            "Only masked padding, pixels",
        ]
        
        if is_update_available:
            self.update_config()

        # components that pass through after_components
        self.all_components = []
 
        # Read saved settings
        PresetManager.all_presets = self.get_config(self.settings_file)

        # Initialize
        self.component_map = {k: None for k in self.available_components}
        self.additional_components_map = {k:None for k in self.additional_components_for_presets["additionalComponents"]}
        self.additional_components = [x for x in self.additional_components_map] # acts like available_components list for additional components

        # combine defaults and choices
        self.component_map = {**self.component_map, **self.additional_components_map}
        self.available_components = self.available_components + self.additional_components


    
    def fakeinit(self, *args, **kwargs):
        """
        __init__ workaround, since some data is not available during instantiation, such as is_img2img, filename, etc.
        This method is called from .show(), as that's the first method ScriptRunner calls after handing some state dat (is_txt2img, is_img2img2)
        """
        #self.elm_prfx = f"{'txt2img' if self.is_txt2img else 'img2img'}"
        self.elm_prfx = "preset-util"


        # UI elements
        # class level
        # NOTE: Would love to use one component rendered twice, but gradio does not allow rendering twice, so I need one per page
        if self.is_txt2img:
            # quick set tab
            PresetManager.txt2img_preset_dropdown = gr.Dropdown(
                label="Presets",
                choices=list(PresetManager.all_presets.keys()),
                render = False,
                elem_id=f"{self.elm_prfx}_preset_qs_dd"
            )
            # Detailed Save
            PresetManager.txt2img_save_detailed_name_dropdown = gr.Dropdown(render=False,
                choices=PresetManager.txt2img_preset_dropdown.choices,
                label="Presets",
                elem_id=f"{self.elm_prfx}_preset_ds_dd"
            )
            #else:
            # quick set tab
            PresetManager.img2img_preset_dropdown = gr.Dropdown(
                label="Presets",
                choices=list(PresetManager.all_presets.keys()),
                render = False,
                elem_id=f"{self.elm_prfx}_preset_qs_dd"
            )
            # Detailed Save
            PresetManager.img2img_save_detailed_name_dropdown = gr.Dropdown(render=False,
                choices=PresetManager.img2img_preset_dropdown.choices,
                label="Presets",
                elem_id=f"{self.elm_prfx}_preset_ds_dd"
            )

        # instance level
        # quick set tab
        self.stackable_check = gr.Checkbox(value=True, label="Stackable", elem_id=f"{self.elm_prfx}_stackable_check", render=False)
        self.save_as = gr.Text(render=False, label="Quick Save", elem_id=f"{self.elm_prfx}_save_qs_txt")
        self.save_button = gr.Button(value="Save", variant="secondary", render=False, visible=False, elem_id=f"{self.elm_prfx}_save_qs_bttn")


        # Detailed Save
        self.stackable_check_det = gr.Checkbox(value=True, label="Stackable", elem_id=f"{self.elm_prfx}_stackable_check_det", render=False)
        self.save_detail_md = gr.Markdown(render=False, value="<center>Options are all options hardcoded, and additional you added in additional_components.py</center>\
            <center>Make your choices, adjust your settings, set a name, save. To edit a prior choice, select from dropdown and overwrite.</center>\
            <center>To apply, go to quick set. Save now works immediately in other tab without restart, filters out non-common between tabs.</center>\
            <center>Settings stack. If it's not checked, it wont overwrite. Apply one, then another. Reset is old, update how you need.</center>\
                <center>Stackable checkbox is not used for saves, it's used when making a selection from the dropdown, whether to apply as stackable or not</center>", elem_id=f"{self.elm_prfx}_mess_qs_md")
        self.save_detailed_as = gr.Text(render=False, label="Detailed Save As", elem_id=f"{self.elm_prfx}_save_ds_txt")
        self.save_detailed_button = gr.Button(value="Save", variant="primary", render=False, visible=False, elem_id=f"{self.elm_prfx}_save_ds_bttn")
        self.save_detailed_delete_button = gr.Button(value="❌Delete", render=False, elem_id=f"{self.elm_prfx}_del_ds_bttn")
        # **********************************           NOTE  ********************************************
        # NOTE: This fix uglified the code ui is now _ui, row created in before_component, stored in var, used in after_component
        # ! TODO: Keep an eye out on this, could cause confusion, if it does, either go single checkboxes with others visible False, or ...
        # Potential place to put this, in after_components elem_id txt_generation_info_button or img2img_generation_info button
        #self.save_detailed_checkbox_group = gr.CheckboxGroup(render=False, choices=list(x for x in self.available_components if self.component_map[x] is not None), elem_id=f"{self.elm_prfx}_select_ds_chckgrp")


        # Restart tab
        self.gr_restart_bttn = gr.Button(value="Restart", variant="primary", render=False, elem_id=f"{self.elm_prfx}_restart_bttn")


        # Print tab
        self.gather_button = gr.Button(value="Gather", render = False, variant="primary", elem_id=f"{self.elm_prfx}_gather_bttn")         # Helper button to print component map
        self.inspect_dd = gr.Dropdown(render = False, type="index", interactive=True, elem_id=f"{self.elm_prfx}_inspect_dd")
        self.inspect_ta = gr.TextArea(render=False, elem_id=f"{self.elm_prfx}_inspect_txt")


        self.info_markdown = gr.Markdown(value="<center>!⚠! THIS IS IN ALPHA !⚠!</center>\n\
<center>🐉 I WILL INTRODUCE SOME BREAKING CHANGES (I will try to avoid it) 🐉</center>\
<center>🙏 Please recommend your favorite script composers to implement element id's 🙏</center>\n\
<br>\
<center>If they implement unique element id's, they can get support for presets without making their own</center>\
<center>❗ I have not added element id support yet, there are more labels than id's ❗</center>\
<br>\
<center>❗❗But labels sometimes collide. I can't do 'Mask Blur' because it also matches 'Mask Blur' in scripts❗❗</center>\
<center>Try adding a component label to additional_components.json with element id 'null' without quotes for None</center>\
<br>\
<center><strong>I would like to support all custom scripts, but need script path/name/title, some distinguishing factor</strong></center>\
<center>through the kwargs in IOComponent_init 'after_compoenet' and 'before_component'</center>\
<center><link>https://github.com/Gerschel/sd_web_ui_preset_utils</link></center>", render=False)


    def title(self):
        return "Presets"

    def show(self, is_img2img):
        self.fakeinit()
        return True
        if self.ui_first == "sampler":
            if shared.opts.samplers_in_dropdown:
                self.before_component_label = "Sampling method"
            else:
                self.before_component_label = "Sampling Steps"
            return True
        else:
            self.before_component_label = self.positon_manager
            return True

    def before_component(self, component, **kwargs):
        pass
    def _before_component(self, component, **kwargs):
        # Define location of where to show up
        #if kwargs.get("elem_id") == "":#f"{'txt2img' if self.is_txt2img else 'img2img'}_progress_bar":
        #print(kwargs.get("label") == self.before_component_label, "TEST", kwargs.get("label"))
        #if kwargs.get("label") == self.before_component_label:
            with gr.Accordion(label="Preset Manager", open = False, elem_id=f"{'txt2img' if self.is_txt2img else 'img2img'}_preset_manager_accordion"):
                # Quick TAB
                with gr.Tab(label="Quick"):
                    with gr.Row(equal_height = True):
                            if self.is_txt2img:
                                PresetManager.txt2img_preset_dropdown.render()
                            else:
                                PresetManager.img2img_preset_dropdown.render()
                            with gr.Column(elem_id=f"{self.elm_prfx}_ref_del_col_qs"):
                                self.stackable_check.render()
                    with gr.Row():
                        with gr.Column(scale=12):
                            self.save_as.render()
                        with gr.Column(scale=1):
                            self.save_button.render()

                # Detailed Save TAB
                with gr.Tab(label="Detailed"):
                    with gr.Accordion(label="Basic info", open=False):
                        self.save_detail_md.render()
                    with gr.Column(scale=1):
                        with gr.Row(equal_height = True):
                            if self.is_txt2img:
                                PresetManager.txt2img_save_detailed_name_dropdown.render()
                            else:
                                PresetManager.img2img_save_detailed_name_dropdown.render()
                            with gr.Column(elem_id=f"{self.elm_prfx}_ref_del_col_ds"):
                                self.save_detailed_delete_button.render()
                                self.stackable_check_det.render()
                        with gr.Row():
                            with gr.Column(scale=12):
                                self.save_detailed_as.render()
                            with gr.Column(scale=1):
                                self.save_detailed_button.render()
                    with gr.Column(scale=1) as detailed_check:
                        self.detailed_check = detailed_check
                        #self.save_detailed_checkbox_group.render()

                # Restart TAB
                with gr.Tab(label="Restart"):
                    self.gr_restart_bttn.render()

                # Print TAB
                with gr.Tab(label = "Print"):
                    self.gather_button.render()
                    self.inspect_dd.render()
                    self.inspect_ta.render()

                # Info TAB
                with gr.Tab(label="Info"):
                    self.info_markdown.render()


    def after_component(self, component, **kwargs):
        if hasattr(component, "label") or hasattr(component, "elem_id"):
            self.all_components.append(self.compinfo(
                                                      component=component,
                                                      label=component.label if hasattr(component, "label") else None,
                                                      elem_id=component.elem_id if hasattr(component, "elem_id") else None,
                                                      kwargs=kwargs
                                                     )
                                      )
        label = kwargs.get("label")
        ele = kwargs.get("elem_id")
        # TODO: element id
        #if label in self.component_map or label in self.additional_components_map:# and ele == self.additional_components["additionalComponents"]) or (ele == self.additional_components["additionalComponents"]):
        if label in self.component_map:# and ele == self.additional_components["additionalComponents"]) or (ele == self.additional_components["additionalComponents"]):
            #!Hack to remove conflict between main Prompt and hr Prompt
            if self.component_map[label] is None:
                self.component_map.update({component.label: component})
        

        if ele == "txt2img_generation_info_button" or ele == "img2img_generation_info_button":
            self._before_component("")
            self.save_detailed_checkbox_group = gr.CheckboxGroup(render=False, choices=list(x for x in self.available_components if self.component_map[x] is not None), elem_id=f"{self.elm_prfx}_select_ds_chckgrp", label="This preset affects?")
            with self.detailed_check:
                self.save_detailed_checkbox_group.render()
            self._ui()

    def ui(self, *args):
        pass

    def _ui(self):

        
        # Conditional for class members
        if self.is_txt2img:
            # Quick Set Tab
            PresetManager.txt2img_preset_dropdown.change(
                fn=self.fetch_valid_values_from_preset,
                inputs=[self.stackable_check, PresetManager.txt2img_preset_dropdown] + [self.component_map[comp_name] for comp_name in list(x for x in self.available_components if self.component_map[x] is not None)],
                outputs=[self.component_map[comp_name] for comp_name in list(x for x in self.available_components if self.component_map[x] is not None)],
            )
            # Detailed save tab
            PresetManager.txt2img_save_detailed_name_dropdown.change(
                fn = self.save_detailed_fetch_valid_values_from_preset,
                inputs = [self.stackable_check_det, PresetManager.txt2img_save_detailed_name_dropdown] + [self.component_map[comp_name] for comp_name in list(x for x in self.available_components if self.component_map[x] is not None)],
                outputs = [self.save_detailed_checkbox_group, self.save_detailed_as] + [self.component_map[comp_name] for comp_name in list(x for x in self.available_components if self.component_map[x] is not None)],
            )
        else:
            # Quick Set Tab
            PresetManager.img2img_preset_dropdown.change(
                fn=self.fetch_valid_values_from_preset,
                inputs=[self.stackable_check, PresetManager.img2img_preset_dropdown] + [self.component_map[comp_name] for comp_name in list(x for x in self.available_components if self.component_map[x] is not None)],
                outputs=[self.component_map[comp_name] for comp_name in list(x for x in self.available_components if self.component_map[x] is not None)],
            )
            # Detailed save tab
            PresetManager.img2img_save_detailed_name_dropdown.change(
                fn = self.save_detailed_fetch_valid_values_from_preset,
                inputs = [self.stackable_check_det, PresetManager.img2img_save_detailed_name_dropdown] + [self.component_map[comp_name] for comp_name in list(x for x in self.available_components if self.component_map[x] is not None)],
                outputs = [self.save_detailed_checkbox_group, self.save_detailed_as] + [self.component_map[comp_name] for comp_name in list(x for x in self.available_components if self.component_map[x] is not None)],
            )

        #Mixed Level use this section when needing to reference a class member for things that will affect both tabs
        #QuickSet Tab
        self.save_button.click(
            fn = self.wrapper_save_config(path=self.settings_file),
            inputs = [self.save_as] + [self.component_map[comp_name] for comp_name in list(x for x in self.available_components if self.component_map[x] is not None)],# if self.component_map[comp_name] is not None],
            outputs = [self.save_as, PresetManager.txt2img_preset_dropdown, PresetManager.img2img_preset_dropdown, PresetManager.txt2img_save_detailed_name_dropdown, PresetManager.img2img_save_detailed_name_dropdown]
            #outputs = [self.save_as, self.preset_dropdown, self.save_detailed_name_dropdown]
        )#Todo: class level components
        #Detailed Tab
        self.save_detailed_button.click(
            fn = self.save_detailed_config(path=self.settings_file),
            # Potential issue
            inputs = [self.save_detailed_as , self.save_detailed_checkbox_group] + [self.component_map[comp_name] for comp_name in list(x for x in self.available_components if self.component_map[x] is not None)],
            outputs = [self.save_detailed_as, PresetManager.txt2img_save_detailed_name_dropdown, PresetManager.img2img_save_detailed_name_dropdown, PresetManager.txt2img_preset_dropdown, PresetManager.img2img_preset_dropdown]
            #outputs = [self.save_detailed_as, self.save_detailed_name_dropdown, self.preset_dropdown]
        )
        self.save_detailed_delete_button.click(
            fn = lambda x: self.delete_preset(x, self.settings_file),
            inputs = PresetManager.txt2img_save_detailed_name_dropdown if self.is_txt2img else PresetManager.img2img_save_detailed_name_dropdown,
            outputs = [PresetManager.txt2img_preset_dropdown, PresetManager.img2img_preset_dropdown, PresetManager.txt2img_save_detailed_name_dropdown, PresetManager.img2img_save_detailed_name_dropdown]
        )


        #Instance level
        #QuickSet Tab
        self.save_as.change(
            fn = lambda x: gr.update(variant = "primary" if bool(x) else "secondary", visible = bool(x)),
            inputs = self.save_as,
            outputs = self.save_button
        )

        # Detailed save tab
        self.save_detailed_as.change(
            fn = lambda x: gr.update(visible = bool(x)),
            inputs = self.save_detailed_as,
            outputs = self.save_detailed_button
        )
        # Restart Tab
        self.gr_restart_bttn.click(fn=self.local_request_restart, _js='restart_reload', inputs=[], outputs=[])

        # Print/Inspect Tab
        self.gather_button.click(
            fn = self.f_b_syncer,
            outputs=[self.inspect_dd, self.gather_button]
        )
        self.inspect_dd.change(
            fn = lambda x: self.inspection_formatter(x),
            inputs = self.inspect_dd,
            outputs = self.inspect_ta,
        )


    def f_b_syncer(self):
        """
        ?Front/Backend synchronizer?
        Not knowing what else to call it, simple idea, rough to figure out. When updating choices on the front-end, back-end isn't updated, make them both match
        https://github.com/gradio-app/gradio/discussions/2848
        """
        self.inspect_dd.choices = [str(x) for x in self.all_components]
        return [gr.update(choices=[str(x) for x in self.all_components]), gr.Button.update(visible=False)]

    
    def inspection_formatter(self, x):
        comp = self.all_components[x]
        text = f"Component Label: {comp.label}\nElement ID: {comp.elem_id}\nComponent: {comp.component}\nAll Info Handed Down: {comp.kwargs}"
        return text


    def run(self, p, *args):
        pass


    def wrapper_save_config(self, path):
        """
            Helper function to utilize closure
        """
        # closure keeps path in memory, it's a hack to get around how click or change expects values to be formatted
        def func(setting_name, *new_setting):
            """
                Formats setting and overwrites file
                input: setting_name is text autoformatted from clicks input
                       new_settings is a tuple (by using packing) of formatted text, outputs from
                            click method must be in same order of labels
            """
            # Format new_setting from tuple of values, and map them to their label
            try:
                return_dict = {}
                #! TODO: This does not work with datasets or highlighted text that use the type of index
                for i,k in enumerate(x for x in self.component_map if self.component_map[x] is not None):
                    if k != "Sampling method" and not hasattr(self.component_map[k], "type"):
                        return_dict.update({k: new_setting[i]})
                    elif k == "Sampling method":
                        return_dict.update({k: modules.sd_samplers.samplers[new_setting[i]].name if self.is_txt2img else  modules.sd_samplers.samplers_for_img2img[new_setting[i]].name})
                    elif self.component_map[k].type == "index":
                        return_dict.update({k: self.component_map[k].choices[new_setting[i]]})
                    else:
                        return_dict.update({k: new_setting[i]})
                new_setting = return_dict

            except IndexError as e:
                print(f"IndexError : {e}\n\
Length: {len(new_setting)}\tvalue: {new_setting}\n\
Length: {len(self.component_map)}\t keys: {list(self.component_map.keys())}\n\
\tvalues: {list(self.component_map.values())}\n\
Length: {len(self.available_components)}\t keys: {self.available_components}")

            file = os.path.join(PresetManager.BASEDIR, path)
            PresetManager.all_presets.update({setting_name : new_setting})
            
            with open(file, "w") as f:
                json.dump(PresetManager.all_presets, f, indent=4)
            #TODO: test [] + [] * 4
            return [gr.update(value=""), gr.update(choices = list(PresetManager.all_presets.keys())), gr.update(choices = list(PresetManager.all_presets.keys())), gr.update(choices = list(PresetManager.all_presets.keys())), gr.update(choices = list(PresetManager.all_presets.keys()))]
        return func
        

    def save_detailed_config(self, path):
        """
            Helper function to utilize closure
        """
        # closure keeps path in memory, it's a hack to get around how click or change expects values to be formatted
        #! ME ************************************************************
        def func(setting_name, *new_setting):
            """
                Formats setting and overwrites file
                input: setting_name is text autoformatted from clicks input
                       new_settings is a tuple (by using packing) of formatted text, outputs from
                            click method must be in same order of labels
            """
            # Format new_setting from tuple of values, and map them to their label
            checkbox_items = new_setting[0]
            checkbox_items = [x for x in checkbox_items if x in list(x for x in self.available_components if self.component_map[x] is not None)]
            items = [y for y in list(zip(new_setting[1:], list(x for x in self.component_map.items() if x[1] is not None))) if y[1][0] in checkbox_items]
            #items[0] is value to save, items[1] is tuple, items[1][0] is key items[1][1] is component
            try:
                return_dict = {}
                #! TODO: This does not work with datasets or highlighted text that use the type of index
                for e in items:
                    if e[1][0] != "Sampling method" and not hasattr(e[1][1], "type"):
                        return_dict.update({e[1][0]: e[0]})
                    elif e[1][0] == "Sampling method":
                        return_dict.update({e[1][0]: modules.sd_samplers.samplers[e[0]].name if self.is_txt2img else  modules.sd_samplers.samplers_for_img2img[e[0]].name})
                    elif e[1][1].type == "index":
                        return_dict.update({e[1][0]: e[1][1].choices[e[0]]})
                    else:
                        return_dict.update({e[1][0]: e[0]})
                new_setting = return_dict

            except IndexError as e:
                print(f"IndexError : {e}\n\
Length: {len(new_setting)}\tvalue: {new_setting}\n\
Length: {len(self.component_map)}\t keys: {list(self.component_map.keys())}\n\
\tvalues: {list(self.component_map.values())}\n\
Length: {len(self.available_components)}\t keys: {self.available_components}")

            file = os.path.join(PresetManager.BASEDIR, path)
            PresetManager.all_presets.update({setting_name : new_setting})
            #TODO: replace with save method
            with open(file, "w") as f:
                json.dump(PresetManager.all_presets, f, indent=4)
            #return [gr.update(value=""), gr.update(choices = list(PresetManager.all_presets.keys())), gr.update(choices = list(PresetManager.all_presets.keys()))]
            return [gr.update(value=""), gr.update(choices = list(PresetManager.all_presets.keys())), gr.update(choices = list(PresetManager.all_presets.keys())), gr.update(choices = list(PresetManager.all_presets.keys())), gr.update(choices = list(PresetManager.all_presets.keys()))]
        return func
 
    def save_config(self, path, data=None, open_mode='w'):
        file = os.path.join(PresetManager.BASEDIR, path)
        try:
            with open(file, "w") as f:
                json.dump(data if data else PresetManager.all_presets, f, indent=4)
        except FileNotFoundError as e:
            print(f"{e}\n{file} not found, check if it exists or if you have moved it.")


    def get_config(self, path, open_mode='r'):
        file = os.path.join(PresetManager.BASEDIR, path)
        try:
            with open(file, open_mode) as f:
                as_dict = json.load(f) 
        except FileNotFoundError as e:
            print(f"{e}\n{file} not found, check if it exists or if you have moved it.")
        return as_dict 
    

    def fetch_valid_values_from_preset(self,stackable_flag,  selection, *comps_vals):
        #print(stackable_flag)
        #print(selection)
        #print(comps_vals)
        """
            Fetches selected preset from dropdown choice and filters valid components from choosen preset
            non-valid components will still have None as the page didn't contain any
        """
        if stackable_flag:
            #        saved value                           if         in  selection                     and    (true if no choices type else true if value in choices else false (got to default))       else          default value
            return [
                #saved value
                PresetManager.all_presets[selection][comp_name] 
                    if (comp_name in PresetManager.all_presets[selection] 
                        and (
                            True if not hasattr(self.component_map[comp_name], "choices") 
                                else 
                                True if PresetManager.all_presets[selection][comp_name] in self.component_map[comp_name].choices 
                                    else False 
                            ) 
                        ) 
                    else 
                        #default value 
                        comps_vals[i]
                        # if it is not an option type
                        if not hasattr(self.component_map[comp_name], "choices") 
                        # otherwise for option types choose based on index if
                        else self.component_map[comp_name].choices[comps_vals[i]] 
                            # it is an index type
                            if type(comps_vals[i]) == int 
                            # otherwise choose default option based on default entry
                            #! So the error that I have is because the custom component that has text input but is of type
                            #! dropdown, has no default, so it returns an empty list
                            else self.component_map[comp_name].choices[self.component_map[comp_name].choices.index(comps_vals[i])]
                                # ^ if it \/ has a proper default
                                if comps_vals[i] in self.component_map[comp_name].choices
                                # otherwise give the first option
                                else None#self.component_map[comp_name].choices[0]
                    for i, comp_name in enumerate(list(x for x in self.available_components if self.component_map[x] is not None and hasattr(self.component_map[x], "value")))]
        else:
            return [
                PresetManager.all_presets[selection][comp_name] 
                    if (comp_name in PresetManager.all_presets[selection] 
                        and (
                            True if not hasattr(self.component_map[comp_name], "choices") 
                                else 
                                True if PresetManager.all_presets[selection][comp_name] in self.component_map[comp_name].choices 
                                    else False 
                            ) 
                        ) 
                    else 
                        self.component_map[comp_name].value
                    for i, comp_name in enumerate(list(x for x in self.available_components if self.component_map[x] is not None and hasattr(self.component_map[x], "value")))]
 

    def save_detailed_fetch_valid_values_from_preset(self, stackable_flag, selection, *comps_vals):
        """
            Fetches selected preset from dropdown choice and filters valid components from choosen preset
            non-valid components will still have None as the page didn't contain any
        """
        return [[ comp_name for comp_name in PresetManager.all_presets[selection] ], gr.update(value = selection)] + self.fetch_valid_values_from_preset(stackable_flag, selection, *comps_vals)

    def delete_preset(self, selection, filepath):
        """Delete preset from local memory and write file with it removed
            filepath is not hardcoded so it can be used with other preset profiles if support gets added for loading additional presets from shares
        """
        #For writing and keeping front-end in sync with back-end
        PresetManager.all_presets.pop(selection)
        #Keep front-end in sync with backend
        PresetManager.txt2img_preset_dropdown.choice = PresetManager.all_presets.keys()
        PresetManager.img2img_preset_dropdown.choice = PresetManager.all_presets.keys()
        PresetManager.txt2img_save_detailed_name_dropdown.choice = PresetManager.all_presets.keys()
        PresetManager.img2img_save_detailed_name_dropdown.choice = PresetManager.all_presets.keys()
        file = os.path.join(PresetManager.BASEDIR, filepath)
        with open(file, 'w') as f:
            json.dump(PresetManager.all_presets, f, indent=4)
        return [gr.Dropdown.update(choices= list(PresetManager.all_presets.keys()), value=list(PresetManager.all_presets.keys())[0])] * 4

    def local_request_restart(self):
        "Restart button"
        shared.state.interrupt()
        shared.state.need_restart = True

