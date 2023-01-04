class PresetManagerDropdownComponent{
    constructor(component){
        this.component = gradioApp().getElementById(component)
    }
    updateDropdown(selection){
        //getElementById("preset-util_preset_ds_dd").querySelector("select").querySelectorAll("option")[1].selected = true;
        //Array.from(this.component.querySelector("select").querySelectorAll("option")).find( e => e.value.includes(selection)).selected = true;
        this.getDropDownOptions().find( e => e.value.includes(selection)).selected = true;
        this.component.querySelector("select").dispatchEvent(new Event("change"));
    }
    getDropDownOptions(asValues=false){
        if (asValues){
            let temp = new Array;
            Array.from(this.component.querySelector("select").querySelectorAll("option")).forEach( opt => temp.push(opt.value))
            return temp
        }
        else{
            return Array.from(this.component.querySelector("select").querySelectorAll("option"))
        }
    }
    getCurrentSelection(){
        return this.component.querySelector("select").value
    }
}

class PresetManagerCheckboxGroupComponent{
    constructor(component){
        this.component = gradioApp().getElementById(component);
        this.checkBoxes = new Object;
        this.setCheckBoxesContainer()
    }
    setCheckBoxesContainer(){
        Array.from(this.component.querySelectorAll("input")).forEach( _input => this.checkBoxes[_input.nextElementSibling.innerText] = _input)
    }
    getCheckBoxes(){
        let response = new Array;
        for (let _component in this.checkBoxes){
            response.push([_component, this.checkBoxes[_component]])
        }
        return response
    }
    setCheckBoxesValues(iterable){
        for (let _componentText in this.checkBoxes){
            this.conditionalToggle(false, this.checkBoxes[_componentText])
        }
        if (iterable instanceof Array){
            setTimeout( () =>
            iterable.forEach( _label => this.conditionalToggle(true, this.checkBoxes[_label])),
            2)
        }
    }
    conditionalToggle(desiredVal, _component){
        //This method behaves like 'set this value to this'
        //Using element.checked = true/false, does not register the change, even if you called change afterwards,
        //  it only sets what it looks like in our case, because there is no form submit, a person then has to click on it twice.
        //Options are to use .click() or dispatch an event
        if (desiredVal != _component.checked){
            _component.dispatchEvent(new Event("change"))//using change event instead of click, in case browser ad-blockers blocks the click method
        }
    }
}
class PresetManagerMover{
    constructor(self, target, onLoadHandler){
        this.presetManager = gradioApp().getElementById(self)
        this.target = gradioApp().getElementById(target)
        this.handler = gradioApp().getElementById(onLoadHandler)
    }
    move(adjacentAt='afterend'){
        /*
        'beforebegin'
            <ele>
            'afterbegin'
                <otherele>
            'beforeend'
            </ele>
        'afterend'
        */
         
        this.target.insertAdjacentElement(adjacentAt, this.presetManager)
    }
    updateTarget(new_target){
        this.target = gradioApp().getElementById(new_target)
    }
}
//function move(){
//        let src = gradioApp().getElementById("txt2img_preset_manager_accordion");
//        //let target = Array.from(gradioApp().querySelectorAll("div")).filter( d => d.hasAttribute("class") ? d.getAttribute("class").split(" ")[0] == "gradio-container": false)[0]
//        //target.insertAdjacentElement("afterbegin", src)
//        let target = gradioApp().getElementById("tab_txt2img");
//}
//document.addEventListener("DOMContentLoaded",() => () => {setTimeout(move, 10000)})

//onUiTabChange( function (...x) {console.log(x)})