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

class Script(scripts.Script):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.comptuple = namedtuple("CompTuple", ["component", "label", "elem_id", "kwargs"])
        self.all_components = []

        self.available_components = [
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
            render = False
            )

        self.save_as = gr.Text(render=False, label="Quick Save")
        self.save_button = gr.Button(value="Save", variant="secondary", render=False, visible=False)


        # Restart tab
        self.gr_restart_bttn = gr.Button(value="Restart", variant="primary", render=False)


        # Print tab
        self.pprint_button = gr.Button(value="Print", render = False)         # Helper button to print component map


    def title(self):
        return "Presets"

    def show(self, is_img2img):
        return True

    def before_component(self, component, **kwargs):
        # Define location of where to show up
        if kwargs.get("label") == "Sampling Steps":
            with gr.Accordion(label="Utils", open = False):
                with gr.Tab(label="Quick Set"):
                    with gr.Row():
                        self.preset_dropdown.render()
                    with gr.Row(equal_height=True):
                        #with gr.Column(scale=9, equal_height=True):
                        self.save_as.render()
                        with gr.Column(scale=1, equal_height=True):
                            self.save_button.render()
                # TODO: create tab
                # TODO: Edit tab
                with gr.Tab(label="Restart"):
                    self.gr_restart_bttn.render()
                with gr.Tab(label = "Print"):
                    gr.Text(value="Prints all components reachable, to console")
                    self.pprint_button.render()
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

        self.preset_dropdown.change(
            fn=self.fetch_valid_values_from_preset,
            show_progress=False,
            inputs=[self.preset_dropdown],
            outputs=[self.component_map[comp_name] for comp_name in list(x for x in self.available_components if self.component_map[x] is not None)]
            )

        self.save_button.click(
            fn = self.save_config(path=self.settings_file),
            inputs = [self.save_as] + [self.component_map[comp_name] for comp_name in list(x for x in self.available_components if self.component_map[x] is not None)],# if self.component_map[comp_name] is not None],
            outputs = [self.save_as, self.preset_dropdown]
        )

        self.save_as.change(
            fn = lambda x: gr.update(variant = "primary" if bool(x) else "secondary", visible = bool(x)),
            inputs = self.save_as,
            outputs = self.save_button
        )
        self.gr_restart_bttn.click(fn=self.local_request_restart, _js='restart_reload', inputs=[], outputs=[])

        self.pprint_button.click(
            fn = lambda: pprint([x._asdict() for x in self.all_components]),
        )


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
            return [gr.update(value=""), gr.update(choices = list(self.all_presets.keys()))]
        return func
        
        
    def get_config(self, path, open_mode='r'):
        file = os.path.join(BASEDIR, path)
        try:
            with open(file, open_mode) as f:
                as_dict = json.load(f) 
        except FileNotFoundError as e:
            print(f"{e}\n{file} not found, check if it exists or if you have moved it.")
        return as_dict 


    def fetch_valid_values_from_preset(self, selection):
        """
            Fetches selected preset from dropdown choice and filters valid components from choosen preset
            non-valid components will still have None as the page didn't contain any
        """
        return [self.all_presets[selection][comp_name] if comp_name in self.all_presets[selection] else self.component_map[comp_name].value for comp_name in list(x for x in self.available_components if self.component_map[x] is not None and hasattr(self.component_map[x], "value"))]


    def local_request_restart(self):
        "Restart button"
        shared.state.interrupt()
        shared.state.need_restart = True

