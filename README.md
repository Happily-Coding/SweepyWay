# SweepyWay Split Keyboard
A truly ergonomic, begginner friendly keyboard.

## Photos & Outputs

left side | right side
-|-
![left](https://happily-coding.github.io/SweepyWay/images/left_pcb-top.png) | ![right](https://happily-coding.github.io/SweepyWay/images/right_pcb-top.png)

[More outputs](https://happily-coding.github.io/SweepyWay/) (images, pdfs, jscads 3d models you can [view and transform to stl](https://neorama.de/))
<!-- 
![left bottom](https://happily-coding.github.io/SweepyWay/images/left_pcb-bottom.png) | ![right bottom](https://happily-coding.github.io/SweepyWay/images/right_pcb-bottom.png)
-->

## Features
* **Beginner friendly**
  * Abundant keys, but in non disruptive places.
* **Truly ergonomic**
  * Aggressive column stagger, like Ferris Sweep, to match how fingers are staggered.
  * Choc V1 keys
    * Very low actuation force switches available (example: nocturnal)
    * Low profile (seamless use without handrest, easier to adjust height without an adjustable desk)
    * ChocV1 spacing (reach the outer columns with less over-stretching)
  * Tenting, negative tilting, adjustable height and hand rest solutions
* **Energy efficient**
  * [Nice!nano](https://nicekeyboards.com/nice-nano) optimised, but any promicro should work (bottom up) 
  * [Nice!view](https://nicekeyboards.com/nice-view) support
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
  * Uses [kicad-automation-scripts](https://github.com/productize/kicad-automation-scripts) and [FreeRouting](https://github.com/freerouting/freerouting) to **automatically route the traces on the PCB**
  * Uses [KiKit](https://github.com/yaqwsx/KiKit) to render PCB previews and production-ready **Gerber files**

## Build Status
[![Build](https://github.com/Happily-Coding/SweepyWay/actions/workflows/build.yaml/badge.svg)](https://github.com/Happily-Coding/SweepyWay/actions/workflows/build.yaml)

<!-- from original repo
## Todo
Mio:
Paso 1: mover todos los electronicos para arriba con mismo ofset
mcu_nice_nano
display_nice_view
battery_connector_jst_ph_2
reset_switch_tht_top
utility_ergogen_logo
version_txt
power_switch_smd_side
polygon arriba

Paso 2: sacar cosas raras/ tratar de simplificar el file

Paso 3:
hay que recrear el area, y reorganizar componentes como mi original
hay que recrear el outline y organizar componentes como el original (pero todavia no)

* Bottom Plate (Thick PCB with cutouts for all components placed at the bottom. Optimised for maximum thinness)
* Remove or document magic numbers
* SMD footrints
* Middle bracked PCB with touchpad (Holds both halves together rigidly)
* stabilizer cutouts Needs more research...
  Thanks https://github.com/jasonhazel for measuring the ChocFox WOB 3u spacebar stabilizer spacing. (40mm)
  watch https://www.youtube.com/watch?v=5tERUZ_BSPM
-->



## How to modify it
<!-- from original repo
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

If you would like to modify this:
* fork it
* clone it locally with celoide submodule git clone --recurse-submodules https://github.com/Happily-Coding/SweepyWay.git
* change `ergogen/config.yaml` to your liking
* reactivate github workflows
* reactivate github pages at https://github.com/your-name/your-repo/settings/pages, choose github actions instead of a branch
* push your changes; the `build.yml` GitHub Workflow will pick it up, autoroute and generate Gerbers, all in a zip file.
  See https://github.com/soundmonster/samoklava/actions
* or:
  * make sure to have Docker CLI and NodeJS installed
  * run `make setup clean all`
  * check the `output` folder for KiCad PCBs and Gerbers
* you can find the latest build artifacts [here](https://happily-coding.github.io/SweepyWay/)

See the [workflow](.github/workflows/build.yml) or the [Makefile](Makefile) for more details.


## Credits
- [mxooaar](https://www.reddit.com/r/ErgoMechKeyboards/comments/1lanvon/comment/mxooaar/) for peaking my interest in actually building my idea for a keyboard
- [christianselig caldera keyboard](https://github.com/christianselig/caldera-keyboard) for showing that creating a custom keyboard was reasonably easy
- [Ergogen](https://github.com/ergogen/ergogen) for the awesome tool for building most of the keyboard
- [Soundmonster Samaklova Keyboard](https://github.com/soundmonster/samoklava/tree/main) for automatic electronic routing
- [tbaumann typematrix](https://github.com/tbaumann/typematrix_split_new/tree/main/ergogen) for automatic documentation, and example of how to use celoide ergonomic footprints
- [Celoide](https://github.com/ceoloide/ergogen-footprints) for the library of additional ergogen footprints for more parts.

## Disclaimer
**Work in progress!**

## Important
Only connect battery if a nice!nano board is used!

## Addittional notes
You can transform jscad files (which are the output of cases for ergogen) to stls (which can be opened by many cad softwares) using https://neorama.de/
Apparently you can open them locally with https://github.com/openscad/openscad/ (but im not sure if the output of ergogen is compatible with the current version). also the current version of https://openjscad.xyz/ does not seem to be compatible