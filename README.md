# sd_web_ui_preset_utils
Release version of preset utilities

To install: Go to settings tab of stable-diffusion-webui, go to install from url, paste in this url and click install:
https://github.com/Gerschel/sd_web_ui_preset_utils

![presets_utility_example1](https://user-images.githubusercontent.com/9631031/207841754-590557c0-b5a9-43ca-a35c-29410c55e42a.gif)


I finally present after some weeks of working on some presettings, an initial release.  
In earlier iterations I had attempted to use gr.Examples, dropdowns, chaining dropdowns, textfields, etc.  
The thing that I had to wrap my head around, was how I needed to modify and containerize some things, how gradio disliked certain
python code in their methods, and work around inconsistent bugs. An example, when sending some updates to some components, on a regular, it works fine, but if
you are doing it in an iteration, some parts are locked in scope, and others are not, in an inconsistent way, where a gr.Dropdown.update would work, and at other
times fail, and you would need to use gr.update instead, this all depends on if you use a list comprehension inside a for loop, in which you also need to use closure. 
You can read about some of it here https://github.com/gradio-app/gradio/discussions/2795 and here https://github.com/gradio-app/gradio/discussions/2769

The initial reason why I got in to this, is because I'm also working on an extended version of my xzy https://github.com/Gerschel/xyz-plot-grid 

EXTENDED VERSION: Not out for release, it was pending this project first. But you could see how it had presets involved.
![image](https://user-images.githubusercontent.com/9631031/207840968-42973716-09cc-4fbb-b308-9b330e4ed57d.png)


In the meantime, I release it as minimally obfuscated code.  

The good news. It looks like I can work with custom scripts settings as well. This will take a little figuring out, and some homework for the user, but shouldn't be much.
