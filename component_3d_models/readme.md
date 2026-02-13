Contains 3d models used to display the 3d file for the keyboard

https://github.com/infused-kim/kb_ergogen_fp/tree/main/3d_models is the source for:
Choc_V1_Keycap_MBK_White_1u
Choc_V1_Hotswap
Choc_V1_Switch
Nice_Nano_V2 (wrl created with https://imagetostl.com/convert/file/step/to/wrl#convert)
PinHeader_2.54mm_2x-12 (needed to make the nice nano hotswapable, covers the sides) PinHeader_2.54mm_2x-12 . The 3 pin header used by nice nano is likely [this one](https://www.digikey.hk/en/models/859444?srsltid=AfmBOopTJoP3wpPMP_HNW_utcFo4uNoQ4fqr97y4B13W0Xm0_5EgGbh_&tab=mfr), or [this one](https://www.digikey.com/en/models/298245?tab=snapmagic) but they are generally unnecessary and [for compatibility with promicro or elite-c its generally better to just go with the side pins ](https://github.com/bstiq/nice-nano-kicad) 
And has others that may be useful (power buttons, pin headers, etc). Could not find the 3d model for the spring headers, but they are slightly less tall, and require 0.8-0.9mm holes (which at some point i verified my pcb already uses by default)

The rest of the pin headers were obtained from: https://kicad.github.io/packages3d/Connector_PinHeader_2.54mm
12 are for promicro compatible, 7 are for xiao ble, 4 are exclusively for RP2040Zero (from waveshare), along with the 10s.

For general purposes. Take look at this: https://kicad.github.io/packages3d/


The step file for the rp zero is from here: https://files.waveshare.com/upload/f/f7/RP2040_Zero_stp.zip

Here you can find the files for xiao ble https://wiki.seeedstudio.com/XIAO_BLE/

It also contaisn instructions with how to use them https://github.com/infused-kim/kb_ergogen_fp but i think nowadays its better to use celoides footprint parameters https://github.com/ceoloide/ergogen-footprints/blob/main/switch_choc_v1_v2.js


https://grabcad.com/library/kailh-low-profile-mechanical-keyboard-switch-1
Choc alternative: kailh-low-profile-mechanical-keyboard-switch-1.snapshot.1 

https://grabcad.com/library/kailh-low-profile-mechanical-keyboard-switch-pg1353-1
choc v2: kailh-low-profile-mechanical-keyboard-switch-pg1353-1.snapshot.6

relegendable keycaps
https://grabcad.com/library/mx-cherry-relegendable-keycaps-1
mx-cherry-relegendable-keycaps-1.snapshot.6

More potentially useful switches https://github.com/kiswitch/kiswitch

3d files for printing dummy chocv2 and v1
https://www.printables.com/model/716753-kaliah-choc-v1-v2-dummy/files

lot more models including silents: https://github.com/koktoh/keyswitch_model

From [the builtin diodes library](https://kicad.github.io/packages3d/Diode_SMD)
D_SOD-123.step 

[from snap magic](https://www.snapeda.com/parts/SSSS811101/ALPS/view-part/?company=-&amp;welcome=home) ALPS power switch SSSS811101--3DModel-STEP-269445

from [componentsearchengnine](https://componentsearchengine.com/part-view/EVQ-PUC02K/Panasonic) EVQ-PUC02K, WRL created with [imagetostl](https://imagetostl.com/convert/file/step/to/wrl#convert)

from [snapmagic](https://www.snapeda.com/parts/S2B-PH-K-S(LF)(SN)/JST/view-part/) the JSTPH2 S2B-PH-K-S(LF)(SN) 3d model, and its wrl created with [imagetostl](https://imagetostl.com/convert/file/step/to/wrl#convert)

IMPORTANT, THE NICE NANO + the headers is still less tall than the switches, but not by much
https://typeractive.xyz/pages/build#corne_choc