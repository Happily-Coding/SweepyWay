# SweepyWay Split Keyboard 

A truly ergonomic, begginner friendly keyboard.

<details open><summary><span style="font-size: 2em; font-weight: bold;">Photos & Outputs</span></summary> 

left side | right side
-|-
![left](https://happily-coding.github.io/SweepyWay/images/left_pcb-top.png) | ![right](https://happily-coding.github.io/SweepyWay/images/right_pcb-top.png)

[More outputs](https://happily-coding.github.io/SweepyWay/) (images, pdfs, stl 3d models, etc)
<!-- 
![left bottom](https://happily-coding.github.io/SweepyWay/images/left_pcb-bottom.png) | ![right bottom](https://happily-coding.github.io/SweepyWay/images/right_pcb-bottom.png)
-->
</details>

<details open><summary><span style="font-size: 2em; font-weight: bold;">Features</span></summary> 

* **Beginner friendly**
  * Available pdfs, so you can print the layout and see how it feels
  * Abundant keys, but in non disruptive places.
* **Truly ergonomic**
  * Aggressive column stagger, like Ferris Sweep, to match how fingers are staggered.
  * Choc V1 keys
    * Very low actuation force switches available (example: nocturnal)
    * Low profile (seamless use without handrest, easier to adjust height without an adjustable desk)
    * ChocV1 spacing (reach the outer columns with less over-stretching)
  * Tenting, negative tilting, adjustable height and hand rest solutions (WIP)
* **Energy efficient**
  * [Nice!nano](https://nicekeyboards.com/nice-nano) optimised, but any promicro should work (bottom up) 
  <!-- * [Nice!view](https://nicekeyboards.com/nice-view) support Not tested, probably requires small modifications --> 
  * No leds
* **Accident prepared** 
  * Controller far away from accidental splash zones,
  * Power switch for transport
  * No metal plates to help prevent static discharge from friying the keyboard
  * Hotswappable battery, switches, keycaps, controller, and case. Replace anything that breaks or you dislike.
    * You can even remove the components and use them with a different pcb.
* **Easy to modify** (Declarative design done via yaml)
  * Layout is declared using [Ergogen](https://github.com/mrzealot/ergogen/). 
  * Uses Ergogen to translate YAML to a KiCad PCB and plate files for FR-4 fab or laser cutting
  * Uses Ergogen to output jscad files for the case, and openjscad to convert them to stl.
  * Uses [kicad-automation-scripts](https://github.com/productize/kicad-automation-scripts) and [FreeRouting](https://github.com/freerouting/freerouting) to **automatically route the traces on the PCB**
  * Uses [KiKit](https://github.com/yaqwsx/KiKit) to render PCB previews and production-ready **Gerber files**
  * Uses [Trimesh](https://github.com/mikedh/trimesh/tree/main) to parametrically create a palm rest for the keyboard shape.
  * Uses Kibot to produce jlpcb pos files and BOM so you can order your pcb assembled and not have to solder. (WIP) 
  * Compatible with [no solder spring headers](https://typeractive.xyz/products/no-solder-spring-headers) 

## Disclaimer:! [![Build](https://github.com/Happily-Coding/SweepyWay/actions/workflows/build.yaml/badge.svg)](https://github.com/Happily-Coding/SweepyWay/actions/workflows/build.yaml)
<details><summary><span style="font-size: 2em; font-weight: bold;"> Work in progress. TODO List:</span></summary> 

- perfect top case, and replicate for right side
  - the controller area is delicate, we need to only increase height on the part that the controller and maybe the jsph and reset switch are, since otherwise they wont fit with the plate cutting into them
  - We need to keep the reset butotn exposed to the outside if we want to be able to use the keyboard flash with the cover on (which may be important for typing)
- add the battery and microcontroller 3d model to check there are no issues
- add a lengua in the wall of the case below the top plate to en sure no drainage on the corners?
- Add parametric tenting legs.
- Add spacing between case wall and pcb (add some more padding in addition to the wall thickness)
- Finish making hand rest parametric and integrate it into the pipeline
- Fix the additional outline to cover the controller
- make sure the bom & pos are outputed correctly and ideally automated
- Nice haves:
  - Make base tilting and tenting compatible and or adjustable height
  - add water draining holes
  - Add a piece of plastic that goes inward from the top of the border and fits in it to cover the pcb
  - add leds and spacing for a big batery in the tenting solution
  - add other controller types
  - improve controller pin assignment for better routing
  - Add headers soldering from jlpcb
  - add a tenting system with space for a larger batery or make space for a larger batery in the palm rest, so you can reasonably use the keyboard with rgb.
  - Add row staggered variants that are space efficient.
  - Make sure the keyboard is correctly produced with mbk spacing, and mx spacing.
  - Add the ability to customize keycap spacing for the outer columns and rows
</details>


<details><summary><span style="font-size: 2em; font-weight: bold;">How to modify it</span></summary> 

### Setup
If you would like to modify this:
* fork it
* clone it locally with celoide submodule git clone --recurse-submodules https://github.com/Happily-Coding/SweepyWay.git
* change `ergogen/config.yaml` to your liking
* reactivate github workflows
* reactivate github pages at https://github.com/your-name/your-repo/settings/pages, choose github actions instead of a branch
* push your changes; the `build.yml` GitHub Workflows(https://github.com/your-name/your-repo/actions) will pick it up, autoroute and generate Gerbers, all in a zip file, and then deploy it to github pages(https://your-name.github.io/your-repo/).
* or:
  * make sure to have Docker CLI and NodeJS installed
  * run `make setup clean all`
  * check the `output` folder for KiCad PCBs and Gerbers
* you can find the latest build artifacts [here](https://happily-coding.github.io/SweepyWay/)

See the [workflow](.github/workflows/build.yml) or the [Makefile](Makefile) for more details.

### Quickly previewing the pcb before pushing
Open the project, open a terminal, run ```cd ergogen``` and ```ergogen .```

### Quickly previewing the case and other jscad files before pushing
Open [neorama openjscad](https://neorama.de/) , and drag the jscad file to the button, you can pan and move using right click or shift rightclick.


### Quickly previewing the palmrest before pushing
- Install uv ```pip install uv``` and run uv sync to generate your virtual environment (only once)
- Run ergogen to produce the outlines.
- ```uv run palmrest_and_tenting_creation/create_palmrest.py```

<!-- 
### Add more keys in places that don't interfere with the controller
Add elements to the row or column matrix, and map them (WIP, TODO explain with more detail)

### Use other controllers

### Use mx switches / chocv2 switches

### Use other battery/reset switches/ footprints
See this examples: 
https://github.com/jsbursik/Janus-Keyboard mx nice nano reversible with custom footprints
https://github.com/tarneaux/triboard xiao controller choc spaced reversible with battery polygon!
https://github.com/Henkru/novum mx with jlpcb target, middle layer for stability, and awesome background art
https://github.com/Musab-Hassan/aurora_keyboard very detailed, and well organized mx example
https://github.com/soundmonster/samoklava/tree/main
https://github.com/christianselig/caldera-keyboard/blob/main/ergogen/config.yaml
https://github.com/jusdisgi/splaveferris/blob/main/ergogen/config.yaml (choc v1, smd) <-- reference for mirrored
https://github.com/jusdisgi/biggie-splays/blob/main/biggie-splays_choc_v1/config.yaml mirror matrix
https://pastebin.com/JzsmATYZ celoide reversible (obtianed from atreus/absolem discord) https://cdn.discordapp.com/attachments/759825860617437204/1376609916986327150/pleiades.yaml?ex=685b8624&is=685a34a4&hm=b6c63e79710fd8ff0cd410843348a5f8570dccdcfe2448ce519ddc2d7e60ecf4&
Complex case, and mounting example with celodie footpritns https://github.com/MalusKnight/SplitMax-Ergogen/blob/main/config.yaml and oleds
https://github.com/Nuclear-Squid/Quacken/blob/main/config.yaml [ro micro non celoide]
https://peterlyons.com/problog/2024/05/kipra-keyboard/ how to load an ergogen otuput to freecad 
https://github.com/johnlamb/LambBT/blob/main/ergogen/config.yaml case, m2 screwes, etc 
https://github.com/AtomicJon/jonkey/blob/main/jonkey-v2.yml other celoide footprints usage
https://github.com/scipioni/clavis alternative stup for auto routing 
#asym in theory can be used in outlines to get only mirrored or only normal points https://docs.ergogen.xyz/outlines/
-->
</details>


## Credits
- [mxooaar](https://www.reddit.com/r/ErgoMechKeyboards/comments/1lanvon/comment/mxooaar/) for peaking my interest in actually building my idea for a keyboard
- [christianselig caldera keyboard](https://github.com/christianselig/caldera-keyboard) for showing that creating a custom keyboard is reasonably easy
- [Ergogen](https://github.com/ergogen/ergogen) for the awesome tool for building most of the keyboard
- [Soundmonster Samaklova Keyboard](https://github.com/soundmonster/samoklava/tree/main) for automatic electronic routing
- [tbaumann typematrix](https://github.com/tbaumann/typematrix_split_new/tree/main/ergogen) for automatic documentation, and example of how to use celoide ergonomic footprints
- [Celoide](https://github.com/ceoloide/ergogen-footprints) for the library of additional ergogen footprints for more parts and the awesome discord.
- [alakuu/skree](https://www.reddit.com/user/alakuu/) for taking the time to answer questions about pcb assembly services
- [Choco-rain](https://www.reddit.com/r/MechanicalKeyboards/comments/qanrr8/corne_with_3d_printed_cases_wrist_rests_and_plates/) for palmrest inspiration
