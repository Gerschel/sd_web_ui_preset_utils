

import gradio as gr
import modules.sd_samplers
import modules.scripts as scripts
from modules import shared
import json
import os
from pprint import pprint
from modules.ui import gr_show
from collections import namedtuple

BASEDIR = scripts.basedir()

#https://github.com/Zyin055 steals my code I did not contribute to use, or give permission to use, because I helped one time, deletes issues I created about copyright theft, while Zyin055 wants to have copyright of theirs.
#This person deleted evidence I posted on their repository when they stated they weren't. https://github.com/Zyin055/Config-Presets/blob/main/scripts/config_presets.py#L334
#https://web.archive.org/web/20221222065632/https://github.com/Zyin055/Config-Presets/issues/12
#https://web.archive.org/web/20221222065708/https://github.com/Zyin055/Config-Presets/issues/13
#https://web.archive.org/web/20221222065656/https://github.com/Zyin055/Config-Presets/issues/14
#https://web.archive.org/web/20221222071917/https://github.com/Zyin055/Config-Presets/pull/5
# issue I posted issue 15, posted more evidence, but it didn't stick becasue I got blocked during submission
# said I never asked about collaborating https://github.com/Zyin055/Config-Presets/pull/1#issuecomment-1348251660

class Script(scripts.Script):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.comptuple = namedtuple("CompTuple", ["component", "label", "elem_id", "kwargs"])
        self.all_components = []

        #self.elm_prfx = f"{'txt2img' if self.is_txt2img else 'img2img'}"
        self.elm_prfx = "preset-util"
        self.available_components = [
            "Negative prompt",
            "Prompt",
            "Sampling Steps",
            "Sampling method",
            "Width",
            "Height",
            "Restore faces",
            "Tiling",
            "Highres. fix",
            "Seed",
            "Extra",
            "Variation seed",
            "Variation strength",
            "Resize seed from width",
            "Resize seed from height",
            "Firstpass width",
            "Firstpass height",
            "Denoising strength",
            "Batch count",
            "Batch size",
            "CFG Scale",
        ]





        self.settings_file = "preset_configuration.json"
        self.additional_settings_file = "additional_components.json"


        self.all_presets = self.get_config(self.settings_file)
        self.additional_components_for_presets = self.get_config(self.additional_settings_file) #additionalComponents


        self.component_map = {k: None for k in self.available_components}
        self.additional_components_map = {k:None for k in self.additional_components_for_presets["additionalComponents"]}
        self.additional_components = [x for x in self.additional_components_map] # acts like available_components list for additional components

        #combine
        self.component_map = {**self.component_map, **self.additional_components_map}
        self.available_components = self.available_components + self.additional_components



        # UI elements
        # quick set tab
        self.preset_dropdown = gr.Dropdown(
            label="Presets",
            choices=list(self.all_presets.keys()),
            render = False,
            elem_id=f"{self.elm_prfx}_preset_qs_dd"
            )

        self.quick_set_refresh_button = gr.Button(value="🔄", render=False, elem_id=f"{self.elm_prfx}_ref_qs_bttn")
        self.quick_set_delete_button = gr.Button(value="❌", render=False, elem_id=f"{self.elm_prfx}_del_qs_bttn")

        self.save_as = gr.Text(render=False, label="Quick Save", elem_id=f"{self.elm_prfx}_save_qs_txt")
        self.save_button = gr.Button(value="Save", variant="secondary", render=False, visible=False, elem_id=f"{self.elm_prfx}_save_qs_bttn")

        # Detailed Save
        self.save_detail_md = gr.Markdown(render=False, value="<center>NOT ALL COMPONENTS APPLY</center><center>Options are all options mixed between tabs, and additional you added in additional_components.py</center>\
            <center>Make your choices, adjust your settings, set a name, save. To edit a prior choice, select from dropdown and overwrite.</center>\
            <center>To apply, go to quick set. New save is not immediately available in other tab without restart (tip, save extra names to overwrite to cheat this)</center>", elem_id=f"{self.elm_prfx}_mess_qs_md")
        self.save_detailed_name_dropdown = gr.Dropdown(render=False, choices=self.preset_dropdown.choices, label="Presets", elem_id=f"{self.elm_prfx}_preset_ds_dd")
        self.save_detailed_refresh_button = gr.Button(value="🔄", elem_id=f"{self.elm_prfx}_ref_ds_bttn")
        self.save_detailed_delete_button = gr.Button(value="❌", render=False, elem_id=f"{self.elm_prfx}_del_ds_bttn")
        self.save_detailed_as = gr.Text(render=False, label="Detailed Save", elem_id=f"{self.elm_prfx}_save_ds_txt")
        self.save_detailed_button = gr.Button(value="Save", variant="primary", render=False, visible=False, elem_id=f"{self.elm_prfx}_save_ds_bttn")
        # ! TODO: Keep an eye out on this, could cause confusion, if it does, either go single checkboxes with others visible False, or ...
        # Potential place to put this, in after_components elem_id txt_generation_info_button or img2img_generation_info button
        self.save_detailed_checkbox_group = gr.CheckboxGroup(render=False, choices=self.available_components, elem_id=f"{self.elm_prfx}_select_ds_chckgrp")



        # Restart tab
        self.gr_restart_bttn = gr.Button(value="Restart", variant="primary", render=False, elem_id=f"{self.elm_prfx}_restart_bttn")


        # Print tab
        self.gather_button = gr.Button(value="Gather", render = False, variant="primary", elem_id=f"{self.elm_prfx}_gather_bttn")         # Helper button to print component map
        self.inspect_dd = gr.Dropdown(render = False, type="index", interactive=True, elem_id=f"{self.elm_prfx}_inspect_dd")
        self.inspect_ta = gr.TextArea(render=False, elem_id=f"{self.elm_prfx}_inspect_txt")

    def title(self):
        return "Presets"

    def show(self, is_img2img):
        return True

    def before_component(self, component, **kwargs):
        # Define location of where to show up
        if kwargs.get("label") == "Sampling Steps":
            with gr.Accordion(label="Utils", open = False):
                with gr.Tab(label="Quick Set"):
                    with gr.Row(equal_height = True):
                        self.preset_dropdown.render()
                        with gr.Column(scale=1, elem_id = f"{self.elm_prfx}_ref_del_col_qs"):
                            self.quick_set_refresh_button.render()
                            self.quick_set_delete_button.render()

                    with gr.Row():
                        with gr.Column(scale=12):
                            self.save_as.render()
                        with gr.Column(scale=1):
                            self.save_button.render()

                # TODO: create tab
                # TODO: Edit tab
                with gr.Tab(label="Detailed Save"):
                    self.save_detail_md.render()
                    with gr.Column(scale=1):
                        with gr.Row(equal_height = True):
                            self.save_detailed_name_dropdown.render()
                            with gr.Column(scale=1, elem_id = f"{self.elm_prfx}_ref_del_col_ds"):
                                self.save_detailed_refresh_button.style(full_width=True)
                                self.save_detailed_refresh_button.render()
                                self.save_detailed_delete_button.render()
                                
                        with gr.Row():
                            with gr.Column(scale=12):
                                self.save_detailed_as.render()
                            with gr.Column(scale=1):
                                self.save_detailed_button.render()

                    with gr.Column(scale=1):
                        self.save_detailed_checkbox_group.render()
                        

                with gr.Tab(label="Restart"):
                    self.gr_restart_bttn.render()

                with gr.Tab(label = "Print"):
                    self.gather_button.render()
                    self.inspect_dd.render()
                    self.inspect_ta.render()

                with gr.Tab(label="Info"):
                    gr.TextArea(value="!!![THIS IS IN ALPHA]!!!\n\
I WILL INTRODUCE SOME BREAKING CHANGES I recommend you tell all your favorite script composers\n\
to put an elem_id on all their components they want to have preset support for if they don't want\n\
to have to make one for their script themselves. Currently it's in it's ugly state, there is no edit\n\
there is no micromanaging settings, element id's not suppported yet (soon). There can be a collision\n\
of names.\n\
Current usage to add your scripts to settings. Open additional_components.json and add the \"label\"\n\
and element id, in json format.\n\
A goal of this script is to manage presets for ALL scripts, with choices of customization of what each preset affects.")



    def after_component(self, component, **kwargs):
        if hasattr(component, "label") or hasattr(component, "elem_id"):
            self.all_components.append(self.comptuple(
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
            self.component_map.update({component.label: component})


    def ui(self, is_img2img):

        # Quick Set Tab
        self.preset_dropdown.change(
            fn=self.fetch_valid_values_from_preset,
            inputs=[self.preset_dropdown],
            outputs=[self.component_map[comp_name] for comp_name in list(x for x in self.available_components if self.component_map[x] is not None)],
            )

        self.save_button.click(
            fn = self.save_config(path=self.settings_file),
            inputs = [self.save_as] + [self.component_map[comp_name] for comp_name in list(x for x in self.available_components if self.component_map[x] is not None)],# if self.component_map[comp_name] is not None],
            outputs = [self.save_as, self.preset_dropdown, self.save_detailed_name_dropdown]
        )

        self.save_as.change(
            fn = lambda x: gr.update(variant = "primary" if bool(x) else "secondary", visible = bool(x)),
            inputs = self.save_as,
            outputs = self.save_button
        )

        self.quick_set_refresh_button.click(
            fn = lambda: self.get_config(self.settings_file, reload=True),
            outputs=[self.preset_dropdown, self.save_detailed_name_dropdown]
        )

        self.quick_set_delete_button.click(
            fn = lambda x: self.delete_preset(x, self.settings_file),
            inputs = self.preset_dropdown,
            outputs = [self.preset_dropdown, self.save_detailed_name_dropdown]
        )


        # Detailed save tab
        self.save_detailed_name_dropdown.change(
            fn = self.save_detailed_fetch_valid_values_from_preset,
            inputs = [self.save_detailed_name_dropdown],
            outputs = self.save_detailed_checkbox_group,
        )

        self.save_detailed_as.change(
            fn = lambda x: gr.update(visible = bool(x)),
            inputs = self.save_detailed_as,
            outputs = self.save_detailed_button
        )

        self.save_detailed_button.click(
            fn = self.save_detailed_config(path=self.settings_file),
            # Potential issue
            inputs = [self.save_detailed_as , self.save_detailed_checkbox_group] + [self.component_map[comp_name] for comp_name in list(x for x in self.available_components if self.component_map[x] is not None)],
            outputs = [self.save_detailed_as, self.save_detailed_name_dropdown, self.preset_dropdown]
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


    def save_config(self, path):
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
            file = os.path.join(BASEDIR, path)
            self.all_presets.update({setting_name : new_setting})
            
            with open(file, "w") as f:
                json.dump(self.all_presets, f, indent=4)
            return [gr.update(value=""), gr.update(choices = list(self.all_presets.keys())), gr.update(choices = list(self.all_presets.keys()))]
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
            file = os.path.join(BASEDIR, path)
            self.all_presets.update({setting_name : new_setting})
            
            with open(file, "w") as f:
                json.dump(self.all_presets, f, indent=4)
            return [gr.update(value=""), gr.update(choices = list(self.all_presets.keys())), gr.update(choices = list(self.all_presets.keys()))]
        return func
 
        
    def get_config(self, path, open_mode='r', reload=False):
        file = os.path.join(BASEDIR, path)
        try:
            with open(file, open_mode) as f:
                as_dict:dict = json.load(f) 
        except FileNotFoundError as e:
            print(f"{e}\n{file} not found, check if it exists or if you have moved it.")
        if not reload:
            return as_dict 
        else:
            print(self.preset_dropdown.choices)
            print(as_dict)
            print(self.all_presets)
            self.all_presets.update(**as_dict)
            self.preset_dropdown.choices = list(as_dict.keys())
            return gr.update(choices = list(self.all_presets.keys()))
    

    def delete_preset(self, selection, filepath):
        self.all_presets.pop(selection)
        with open(filepath, 'w') as f:
            json.dump(self.all_presets, f, indent=4)
        return [gr.update(choices = list(self.all_presets.keys())), gr.update(choices = list(self.all_presets.keys()))] 

        
    def fetch_valid_values_from_preset(self, selection):
        print(selection)
        """
            Fetches selected preset from dropdown choice and filters valid components from choosen preset
            non-valid components will still have None as the page didn't contain any
        """
        #        saved value                           if         in  selection                     and    (true if no choices type else true if value in choices else false (got to default))       else          default value
        return [self.all_presets[selection][comp_name] if (comp_name in self.all_presets[selection] and (True if not hasattr(self.component_map, "choices") else True if self.all_presets[selection[comp_name]] in self.component_map[comp_name].get("choices", []) else False ) ) else self.component_map[comp_name].value for comp_name in list(x for x in self.available_components if self.component_map[x] is not None and hasattr(self.component_map[x], "value"))]

    def save_detailed_fetch_valid_values_from_preset(self, selection):
        """
            Fetches selected preset from dropdown choice and filters valid components from choosen preset
            non-valid components will still have None as the page didn't contain any
        """
        return [ comp_name for comp_name in self.all_presets[selection] ]




    def local_request_restart(self):
        "Restart button"
        shared.state.interrupt()
        shared.state.need_restart = True

