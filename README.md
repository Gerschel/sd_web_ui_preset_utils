# Because the webui does a git reset --hard, your configs could be overwritten if you are updating. I have implemented a quick and dirty workaround
That applies now and would avoid it on next update  
The quick and dirty workaround will not apply on a soft restart, you will need to do a hard restart  
New installs will face the same problem  

I will rework this when I get a chance.

Would you believe me if I told you I'm not a programmer, but a carpenter.

To install: Go to settings tab of stable-diffusion-webui, go to install from url, paste in this url and click install:
https://github.com/Gerschel/sd_web_ui_preset_utils

Update now brings dropdown updates correctly on save.
Print button uses correct labels when exploring reachable components
Example provided in additional_config.json, example works with presetting original xy and my xyz.
When dropdown type is index, it properly saves the choosen name, so it can update the value properly.

Shameless plug, xyz works with this project -> https://github.com/Gerschel/xyz-plot-grid
UPDATE 2022/12/20: NOW WITH DETAILED SAVE, can use to edit previous settings, do yourself a favor and save a few extra for overwriting for jumping between tabs
![image](https://user-images.githubusercontent.com/9631031/208656774-7e1dc5a5-8459-48cd-8787-eb4335726b64.png)

This gif is outdated, but you get the idea still.
![presets_utility_example1](https://user-images.githubusercontent.com/9631031/207841754-590557c0-b5a9-43ca-a35c-29410c55e42a.gif)

