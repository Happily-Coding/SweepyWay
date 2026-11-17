function r_case_bottom_extrude_3_outline_fn(){
    return new CSG.Path2D([[303,-148],[313,-148]]).appendArc([320,-141],{"radius":7,"clockwise":false,"large":false}).appendPoint([320,-125]).appendArc([319.98212,-124.5],{"radius":7,"clockwise":false,"large":false}).appendArc([320,-124],{"radius":7,"clockwise":false,"large":false}).appendPoint([320,-108]).appendArc([319.98212,-107.5],{"radius":7,"clockwise":false,"large":false}).appendArc([320,-107],{"radius":7,"clockwise":false,"large":false}).appendPoint([320,-91]).appendArc([319.98212,-90.5],{"radius":7,"clockwise":false,"large":false}).appendArc([320,-90],{"radius":7,"clockwise":false,"large":false}).appendPoint([320,-74]).appendArc([313,-67],{"radius":7,"clockwise":false,"large":false}).appendPoint([302.4371966,-67]).appendArc([296,-62.75],{"radius":7,"clockwise":false,"large":false}).appendPoint([286,-62.75]).appendPoint([286,-58.53]).appendArc([279.25,-51.5344657],{"radius":7,"clockwise":false,"large":false}).appendPoint([279.25,-40.77]).appendArc([272.25,-33.77],{"radius":7,"clockwise":false,"large":false}).appendPoint([228.25,-33.77]).appendArc([221.25,-40.77],{"radius":7,"clockwise":false,"large":false}).appendPoint([221.25,-49.8592048]).appendArc([218,-55.77],{"radius":7,"clockwise":false,"large":false}).appendPoint([218,-61.73]).appendPoint([212,-61.73]).appendArc([205,-68.73],{"radius":7,"clockwise":false,"large":false}).appendPoint([205,-75.33]).appendPoint([195,-75.33]).appendArc([188,-82.33],{"radius":7,"clockwise":false,"large":false}).appendPoint([188,-98.33]).appendArc([188.01788,-98.83],{"radius":7,"clockwise":false,"large":false}).appendArc([188,-99.33],{"radius":7,"clockwise":false,"large":false}).appendPoint([188,-115.33]).appendArc([188.01788,-115.83],{"radius":7,"clockwise":false,"large":false}).appendArc([188,-116.33],{"radius":7,"clockwise":false,"large":false}).appendPoint([188,-132.33]).appendArc([195,-139.33],{"radius":7,"clockwise":false,"large":false}).appendPoint([201.4164361,-139.33]).appendPoint([199.4395359,-140.2518437]).appendArc([198.1335481,-141.0448171],{"radius":7,"clockwise":false,"large":false}).appendArc([196.7348985,-141.6597889],{"radius":7,"clockwise":false,"large":false}).appendPoint([182.8784921,-149.6597889]).appendArc([180.3163143,-159.2219667],{"radius":7,"clockwise":false,"large":false}).appendPoint([188.3163143,-173.0783731]).appendArc([197.8784921,-175.6405509],{"radius":7,"clockwise":false,"large":false}).appendPoint([211.7348985,-167.6405509]).appendArc([211.9205907,-167.52948],{"radius":7,"clockwise":false,"large":false}).appendArc([212.1180838,-167.4410773],{"radius":7,"clockwise":false,"large":false}).appendPoint([226.2965972,-160.8295279]).appendPoint([241.7031847,-158.1129309]).appendArc([241.7045303,-158.1126934],{"radius":4,"clockwise":false,"large":false}).appendArc([247.3813017,-150.0037394],{"radius":7,"clockwise":false,"large":false}).appendPoint([245.4961294,-139.3123961]).appendArc([250.4034711,-136.78],{"radius":7,"clockwise":false,"large":false}).appendPoint([256,-136.78]).appendPoint([256,-142.53]).appendArc([263,-149.53],{"radius":7,"clockwise":false,"large":false}).appendPoint([273,-149.53]).appendPoint([273,-153.75]).appendArc([280,-160.75],{"radius":7,"clockwise":false,"large":false}).appendPoint([296,-160.75]).appendArc([303,-153.75],{"radius":7,"clockwise":false,"large":false}).appendPoint([303,-148]).close().innerToCAG()
.subtract(
    CAG.circle({"center":[208.2895731,-160.2956003],"radius":1.1})
.union(
    CAG.circle({"center":[211.2,-132.63],"radius":1.1})
).union(
    CAG.circle({"center":[211.2,-80.13],"radius":1.1})
).union(
    CAG.circle({"center":[296.2,-137.15],"radius":1.1})
).union(
    CAG.circle({"center":[296.2,-86.15],"radius":1.1})
)).extrude({ offset: [0, 0, 3] });
}


function r_case_border_extrude_11_2_outline_fn(){
    return new CSG.Path2D([[303,-148],[313,-148]]).appendArc([320,-141],{"radius":7,"clockwise":false,"large":false}).appendPoint([320,-125]).appendArc([319.98212,-124.5],{"radius":7,"clockwise":false,"large":false}).appendArc([320,-124],{"radius":7,"clockwise":false,"large":false}).appendPoint([320,-108]).appendArc([319.98212,-107.5],{"radius":7,"clockwise":false,"large":false}).appendArc([320,-107],{"radius":7,"clockwise":false,"large":false}).appendPoint([320,-91]).appendArc([319.98212,-90.5],{"radius":7,"clockwise":false,"large":false}).appendArc([320,-90],{"radius":7,"clockwise":false,"large":false}).appendPoint([320,-74]).appendArc([313,-67],{"radius":7,"clockwise":false,"large":false}).appendPoint([302.4371966,-67]).appendArc([296,-62.75],{"radius":7,"clockwise":false,"large":false}).appendPoint([286,-62.75]).appendPoint([286,-58.53]).appendArc([279.25,-51.5344657],{"radius":7,"clockwise":false,"large":false}).appendPoint([279.25,-40.77]).appendArc([272.25,-33.77],{"radius":7,"clockwise":false,"large":false}).appendPoint([228.25,-33.77]).appendArc([221.25,-40.77],{"radius":7,"clockwise":false,"large":false}).appendPoint([221.25,-49.8592048]).appendArc([218,-55.77],{"radius":7,"clockwise":false,"large":false}).appendPoint([218,-61.73]).appendPoint([212,-61.73]).appendArc([205,-68.73],{"radius":7,"clockwise":false,"large":false}).appendPoint([205,-75.33]).appendPoint([195,-75.33]).appendArc([188,-82.33],{"radius":7,"clockwise":false,"large":false}).appendPoint([188,-98.33]).appendArc([188.01788,-98.83],{"radius":7,"clockwise":false,"large":false}).appendArc([188,-99.33],{"radius":7,"clockwise":false,"large":false}).appendPoint([188,-115.33]).appendArc([188.01788,-115.83],{"radius":7,"clockwise":false,"large":false}).appendArc([188,-116.33],{"radius":7,"clockwise":false,"large":false}).appendPoint([188,-132.33]).appendArc([195,-139.33],{"radius":7,"clockwise":false,"large":false}).appendPoint([201.4164361,-139.33]).appendPoint([199.4395359,-140.2518437]).appendArc([198.1335481,-141.0448171],{"radius":7,"clockwise":false,"large":false}).appendArc([196.7348985,-141.6597889],{"radius":7,"clockwise":false,"large":false}).appendPoint([182.8784921,-149.6597889]).appendArc([180.3163143,-159.2219667],{"radius":7,"clockwise":false,"large":false}).appendPoint([188.3163143,-173.0783731]).appendArc([197.8784921,-175.6405509],{"radius":7,"clockwise":false,"large":false}).appendPoint([211.7348985,-167.6405509]).appendArc([211.9205907,-167.52948],{"radius":7,"clockwise":false,"large":false}).appendArc([212.1180838,-167.4410773],{"radius":7,"clockwise":false,"large":false}).appendPoint([226.2965972,-160.8295279]).appendPoint([241.7031847,-158.1129309]).appendArc([241.7045303,-158.1126934],{"radius":4,"clockwise":false,"large":false}).appendArc([247.3813017,-150.0037394],{"radius":7,"clockwise":false,"large":false}).appendPoint([245.4961294,-139.3123961]).appendArc([250.4034711,-136.78],{"radius":7,"clockwise":false,"large":false}).appendPoint([256,-136.78]).appendPoint([256,-142.53]).appendArc([263,-149.53],{"radius":7,"clockwise":false,"large":false}).appendPoint([273,-149.53]).appendPoint([273,-153.75]).appendArc([280,-160.75],{"radius":7,"clockwise":false,"large":false}).appendPoint([296,-160.75]).appendArc([303,-153.75],{"radius":7,"clockwise":false,"large":false}).appendPoint([303,-148]).close().innerToCAG()
.subtract(
    new CSG.Path2D([[301,-146],[313,-146]]).appendArc([318,-141],{"radius":5,"clockwise":false,"large":false}).appendPoint([318,-125]).appendArc([317.9749372,-124.5],{"radius":5,"clockwise":false,"large":false}).appendArc([318,-124],{"radius":5,"clockwise":false,"large":false}).appendPoint([318,-108]).appendArc([317.9749372,-107.5],{"radius":5,"clockwise":false,"large":false}).appendArc([318,-107],{"radius":5,"clockwise":false,"large":false}).appendPoint([318,-91]).appendArc([317.9749372,-90.5],{"radius":5,"clockwise":false,"large":false}).appendArc([318,-90],{"radius":5,"clockwise":false,"large":false}).appendPoint([318,-74]).appendArc([313,-69],{"radius":5,"clockwise":false,"large":false}).appendPoint([300.94343,-69]).appendArc([296,-64.75],{"radius":5,"clockwise":false,"large":false}).appendPoint([284,-64.75]).appendPoint([284,-58.53]).appendArc([279,-53.53],{"radius":5,"clockwise":false,"large":false}).appendPoint([277.25,-53.53]).appendPoint([277.25,-40.77]).appendArc([272.25,-35.77],{"radius":5,"clockwise":false,"large":false}).appendPoint([228.25,-35.77]).appendArc([223.25,-40.77],{"radius":5,"clockwise":false,"large":false}).appendPoint([223.25,-51.0862515]).appendArc([220,-55.77],{"radius":5,"clockwise":false,"large":false}).appendPoint([220,-63.73]).appendPoint([212,-63.73]).appendArc([207,-68.73],{"radius":5,"clockwise":false,"large":false}).appendPoint([207,-77.33]).appendPoint([195,-77.33]).appendArc([190,-82.33],{"radius":5,"clockwise":false,"large":false}).appendPoint([190,-98.33]).appendArc([190.0250628,-98.83],{"radius":5,"clockwise":false,"large":false}).appendArc([190,-99.33],{"radius":5,"clockwise":false,"large":false}).appendPoint([190,-115.33]).appendArc([190.0250628,-115.83],{"radius":5,"clockwise":false,"large":false}).appendArc([190,-116.33],{"radius":5,"clockwise":false,"large":false}).appendPoint([190,-132.33]).appendArc([195,-137.33],{"radius":5,"clockwise":false,"large":false}).appendPoint([207.2629123,-137.33]).appendArc([207.8591932,-138.5324488],{"radius":5,"clockwise":false,"large":false}).appendPoint([200.2847725,-142.0644592]).appendArc([199.0773315,-142.8578081],{"radius":5,"clockwise":false,"large":false}).appendArc([197.7348985,-143.3918397],{"radius":5,"clockwise":false,"large":false}).appendPoint([183.8784921,-151.3918397]).appendArc([182.0483651,-158.2219667],{"radius":5,"clockwise":false,"large":false}).appendPoint([190.0483651,-172.0783731]).appendArc([196.8784921,-173.9085001],{"radius":5,"clockwise":false,"large":false}).appendPoint([210.7348985,-165.9085001]).appendArc([210.993486,-165.7485284],{"radius":5,"clockwise":false,"large":false}).appendArc([211.2728473,-165.6284617],{"radius":5,"clockwise":false,"large":false}).appendPoint([225.6899964,-158.9056348]).appendPoint([241.3558883,-156.1433154]).appendArc([245.4116862,-150.3510357],{"radius":5,"clockwise":false,"large":false}).appendPoint([243.1157264,-137.33]).appendPoint([245,-137.33]).appendArc([249.3586122,-134.78],{"radius":5,"clockwise":false,"large":false}).appendPoint([258,-134.78]).appendPoint([258,-142.53]).appendArc([263,-147.53],{"radius":5,"clockwise":false,"large":false}).appendPoint([275,-147.53]).appendPoint([275,-153.75]).appendArc([280,-158.75],{"radius":5,"clockwise":false,"large":false}).appendPoint([296,-158.75]).appendArc([301,-153.75],{"radius":5,"clockwise":false,"large":false}).appendPoint([301,-146]).close().innerToCAG()
).extrude({ offset: [0, 0, 11.2] });
}


function r_usbc_border_outline_extrude_8_2_outline_fn(){
    return new CSG.Path2D([[250.75,-55.27],[265.75,-55.27]]).appendPoint([265.75,-40.27]).appendPoint([250.75,-40.27]).appendPoint([250.75,-55.27]).close().innerToCAG()
.extrude({ offset: [0, 0, 8.2] });
}


function r_coverpart_switch_plate_outline_extrude_3_outline_fn(){
    return new CSG.Path2D([[299,-144],[313,-144]]).appendArc([316,-141],{"radius":3,"clockwise":false,"large":false}).appendPoint([316,-125]).appendArc([315.9580399,-124.5],{"radius":3,"clockwise":false,"large":false}).appendArc([316,-124],{"radius":3,"clockwise":false,"large":false}).appendPoint([316,-108]).appendArc([315.9580399,-107.5],{"radius":3,"clockwise":false,"large":false}).appendArc([316,-107],{"radius":3,"clockwise":false,"large":false}).appendPoint([316,-91]).appendArc([315.9580399,-90.5],{"radius":3,"clockwise":false,"large":false}).appendArc([316,-90],{"radius":3,"clockwise":false,"large":false}).appendPoint([316,-74]).appendArc([313,-71],{"radius":3,"clockwise":false,"large":false}).appendPoint([299,-71]).appendPoint([299,-69.75]).appendArc([296,-66.75],{"radius":3,"clockwise":false,"large":false}).appendPoint([282,-66.75]).appendPoint([282,-58.53]).appendArc([279,-55.53],{"radius":3,"clockwise":false,"large":false}).appendPoint([263,-55.53]).appendArc([260,-58.53],{"radius":3,"clockwise":false,"large":false}).appendPoint([260,-59.78]).appendPoint([246,-59.78]).appendArc([243.033942,-62.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([229,-62.33]).appendArc([226,-65.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([226,-65.73]).appendPoint([212,-65.73]).appendArc([209,-68.73],{"radius":3,"clockwise":false,"large":false}).appendPoint([209,-79.33]).appendPoint([195,-79.33]).appendArc([192,-82.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([192,-98.33]).appendArc([192.0419601,-98.83],{"radius":3,"clockwise":false,"large":false}).appendArc([192,-99.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([192,-115.33]).appendArc([192.0419601,-115.83],{"radius":3,"clockwise":false,"large":false}).appendArc([192,-116.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([192,-132.33]).appendArc([195,-135.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([209,-135.33]).appendPoint([209,-135.73]).appendArc([212,-138.73],{"radius":3,"clockwise":false,"large":false}).appendPoint([212.1679465,-138.73]).appendPoint([201.130009,-143.8770748]).appendArc([200.0506976,-144.727627],{"radius":3,"clockwise":false,"large":false}).appendArc([198.7348985,-145.1238905],{"radius":3,"clockwise":false,"large":false}).appendPoint([184.8784921,-153.1238905]).appendArc([183.7804159,-157.2219667],{"radius":3,"clockwise":false,"large":false}).appendPoint([191.7804159,-171.0783731]).appendArc([195.8784921,-172.1764493],{"radius":3,"clockwise":false,"large":false}).appendPoint([209.7348985,-164.1764493]).appendArc([210.0614963,-163.9581925],{"radius":3,"clockwise":false,"large":false}).appendArc([210.4276108,-163.8158462],{"radius":3,"clockwise":false,"large":false}).appendPoint([224.9285354,-157.053954]).appendArc([225.0819068,-156.9770215],{"radius":3,"clockwise":false,"large":false}).appendArc([225.2516679,-156.9520707],{"radius":3,"clockwise":false,"large":false}).appendPoint([241.008592,-154.1736999]).appendArc([243.4420707,-150.6983321],{"radius":3,"clockwise":false,"large":false}).appendPoint([240.7322192,-135.33]).appendPoint([245,-135.33]).appendArc([247.966058,-132.78],{"radius":3,"clockwise":false,"large":false}).appendPoint([260,-132.78]).appendPoint([260,-142.53]).appendArc([263,-145.53],{"radius":3,"clockwise":false,"large":false}).appendPoint([277,-145.53]).appendPoint([277,-153.75]).appendArc([280,-156.75],{"radius":3,"clockwise":false,"large":false}).appendPoint([296,-156.75]).appendArc([299,-153.75],{"radius":3,"clockwise":false,"large":false}).appendPoint([299,-144]).close().innerToCAG()
.subtract(
    CAG.circle({"center":[208.2895731,-160.2956003],"radius":1.1})
.union(
    CAG.circle({"center":[211.2,-132.63],"radius":1.1})
).union(
    CAG.circle({"center":[211.2,-80.13],"radius":1.1})
).union(
    CAG.circle({"center":[296.2,-137.15],"radius":1.1})
).union(
    CAG.circle({"center":[296.2,-86.15],"radius":1.1})
).union(
    new CSG.Path2D([[194.7445175,-168.2123477],[206.8688731,-161.2123477]]).appendPoint([199.8688731,-149.0879921]).appendPoint([187.7445175,-156.0879921]).appendPoint([194.7445175,-168.2123477]).close().innerToCAG()
).union(
    new CSG.Path2D([[209.6434455,-159.7679967],[222.3317545,-153.8513411]]).appendPoint([216.4150989,-141.1630321]).appendPoint([203.7267899,-147.0796877]).appendPoint([209.6434455,-159.7679967]).close().innerToCAG()
).union(
    new CSG.Path2D([[225.541883,-152.8391915],[239.3291915,-150.408117]]).appendPoint([236.898117,-136.6208085]).appendPoint([223.1108085,-139.051883]).appendPoint([225.541883,-152.8391915]).close().innerToCAG()
).union(
    new CSG.Path2D([[196,-97.33],[210,-97.33]]).appendPoint([210,-83.33]).appendPoint([196,-83.33]).appendPoint([196,-97.33]).close().innerToCAG()
).union(
    new CSG.Path2D([[196,-114.33],[210,-114.33]]).appendPoint([210,-100.33]).appendPoint([196,-100.33]).appendPoint([196,-114.33]).close().innerToCAG()
).union(
    new CSG.Path2D([[196,-131.33],[210,-131.33]]).appendPoint([210,-117.33]).appendPoint([196,-117.33]).appendPoint([196,-131.33]).close().innerToCAG()
).union(
    new CSG.Path2D([[213,-83.73],[227,-83.73]]).appendPoint([227,-69.73]).appendPoint([213,-69.73]).appendPoint([213,-83.73]).close().innerToCAG()
).union(
    new CSG.Path2D([[213,-100.73],[227,-100.73]]).appendPoint([227,-86.73]).appendPoint([213,-86.73]).appendPoint([213,-100.73]).close().innerToCAG()
).union(
    new CSG.Path2D([[213,-117.73],[227,-117.73]]).appendPoint([227,-103.73]).appendPoint([213,-103.73]).appendPoint([213,-117.73]).close().innerToCAG()
).union(
    new CSG.Path2D([[213,-134.73],[227,-134.73]]).appendPoint([227,-120.73]).appendPoint([213,-120.73]).appendPoint([213,-134.73]).close().innerToCAG()
).union(
    new CSG.Path2D([[230,-80.33],[244,-80.33]]).appendPoint([244,-66.33]).appendPoint([230,-66.33]).appendPoint([230,-80.33]).close().innerToCAG()
).union(
    new CSG.Path2D([[230,-97.33],[244,-97.33]]).appendPoint([244,-83.33]).appendPoint([230,-83.33]).appendPoint([230,-97.33]).close().innerToCAG()
).union(
    new CSG.Path2D([[230,-114.33],[244,-114.33]]).appendPoint([244,-100.33]).appendPoint([230,-100.33]).appendPoint([230,-114.33]).close().innerToCAG()
).union(
    new CSG.Path2D([[230,-131.33],[244,-131.33]]).appendPoint([244,-117.33]).appendPoint([230,-117.33]).appendPoint([230,-131.33]).close().innerToCAG()
).union(
    new CSG.Path2D([[247,-77.78],[261,-77.78]]).appendPoint([261,-63.78]).appendPoint([247,-63.78]).appendPoint([247,-77.78]).close().innerToCAG()
).union(
    new CSG.Path2D([[247,-94.78],[261,-94.78]]).appendPoint([261,-80.78]).appendPoint([247,-80.78]).appendPoint([247,-94.78]).close().innerToCAG()
).union(
    new CSG.Path2D([[247,-111.78],[261,-111.78]]).appendPoint([261,-97.78]).appendPoint([247,-97.78]).appendPoint([247,-111.78]).close().innerToCAG()
).union(
    new CSG.Path2D([[247,-128.78],[261,-128.78]]).appendPoint([261,-114.78]).appendPoint([247,-114.78]).appendPoint([247,-128.78]).close().innerToCAG()
).union(
    new CSG.Path2D([[264,-73.53],[278,-73.53]]).appendPoint([278,-59.53]).appendPoint([264,-59.53]).appendPoint([264,-73.53]).close().innerToCAG()
).union(
    new CSG.Path2D([[264,-90.53],[278,-90.53]]).appendPoint([278,-76.53]).appendPoint([264,-76.53]).appendPoint([264,-90.53]).close().innerToCAG()
).union(
    new CSG.Path2D([[264,-107.53],[278,-107.53]]).appendPoint([278,-93.53]).appendPoint([264,-93.53]).appendPoint([264,-107.53]).close().innerToCAG()
).union(
    new CSG.Path2D([[264,-124.53],[278,-124.53]]).appendPoint([278,-110.53]).appendPoint([264,-110.53]).appendPoint([264,-124.53]).close().innerToCAG()
).union(
    new CSG.Path2D([[264,-141.53],[278,-141.53]]).appendPoint([278,-127.53]).appendPoint([264,-127.53]).appendPoint([264,-141.53]).close().innerToCAG()
).union(
    new CSG.Path2D([[281,-84.75],[295,-84.75]]).appendPoint([295,-70.75]).appendPoint([281,-70.75]).appendPoint([281,-84.75]).close().innerToCAG()
).union(
    new CSG.Path2D([[281,-101.75],[295,-101.75]]).appendPoint([295,-87.75]).appendPoint([281,-87.75]).appendPoint([281,-101.75]).close().innerToCAG()
).union(
    new CSG.Path2D([[281,-118.75],[295,-118.75]]).appendPoint([295,-104.75]).appendPoint([281,-104.75]).appendPoint([281,-118.75]).close().innerToCAG()
).union(
    new CSG.Path2D([[281,-135.75],[295,-135.75]]).appendPoint([295,-121.75]).appendPoint([281,-121.75]).appendPoint([281,-135.75]).close().innerToCAG()
).union(
    new CSG.Path2D([[281,-152.75],[295,-152.75]]).appendPoint([295,-138.75]).appendPoint([281,-138.75]).appendPoint([281,-152.75]).close().innerToCAG()
).union(
    new CSG.Path2D([[298,-89],[312,-89]]).appendPoint([312,-75]).appendPoint([298,-75]).appendPoint([298,-89]).close().innerToCAG()
).union(
    new CSG.Path2D([[298,-106],[312,-106]]).appendPoint([312,-92]).appendPoint([298,-92]).appendPoint([298,-106]).close().innerToCAG()
).union(
    new CSG.Path2D([[298,-123],[312,-123]]).appendPoint([312,-109]).appendPoint([298,-109]).appendPoint([298,-123]).close().innerToCAG()
).union(
    new CSG.Path2D([[298,-140],[312,-140]]).appendPoint([312,-126]).appendPoint([298,-126]).appendPoint([298,-140]).close().innerToCAG()
)).extrude({ offset: [0, 0, 3] });
}


function r_pcb_outline_extrude_1_outline_fn(){
    return new CSG.Path2D([[299,-144],[313,-144]]).appendArc([316,-141],{"radius":3,"clockwise":false,"large":false}).appendPoint([316,-125]).appendArc([315.9580399,-124.5],{"radius":3,"clockwise":false,"large":false}).appendArc([316,-124],{"radius":3,"clockwise":false,"large":false}).appendPoint([316,-108]).appendArc([315.9580399,-107.5],{"radius":3,"clockwise":false,"large":false}).appendArc([316,-107],{"radius":3,"clockwise":false,"large":false}).appendPoint([316,-91]).appendArc([315.9580399,-90.5],{"radius":3,"clockwise":false,"large":false}).appendArc([316,-90],{"radius":3,"clockwise":false,"large":false}).appendPoint([316,-74]).appendArc([313,-71],{"radius":3,"clockwise":false,"large":false}).appendPoint([299,-71]).appendPoint([299,-69.75]).appendArc([296,-66.75],{"radius":3,"clockwise":false,"large":false}).appendPoint([282,-66.75]).appendPoint([282,-58.53]).appendArc([279,-55.53],{"radius":3,"clockwise":false,"large":false}).appendPoint([275.25,-55.53]).appendPoint([275.25,-40.77]).appendArc([272.25,-37.77],{"radius":3,"clockwise":false,"large":false}).appendPoint([228.25,-37.77]).appendArc([225.25,-40.77],{"radius":3,"clockwise":false,"large":false}).appendPoint([225.25,-52.77]).appendPoint([225,-52.77]).appendArc([222,-55.77],{"radius":3,"clockwise":false,"large":false}).appendPoint([222,-65.73]).appendPoint([212,-65.73]).appendArc([209,-68.73],{"radius":3,"clockwise":false,"large":false}).appendPoint([209,-79.33]).appendPoint([195,-79.33]).appendArc([192,-82.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([192,-98.33]).appendArc([192.0419601,-98.83],{"radius":3,"clockwise":false,"large":false}).appendArc([192,-99.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([192,-115.33]).appendArc([192.0419601,-115.83],{"radius":3,"clockwise":false,"large":false}).appendArc([192,-116.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([192,-132.33]).appendArc([195,-135.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([209,-135.33]).appendPoint([209,-135.73]).appendArc([212,-138.73],{"radius":3,"clockwise":false,"large":false}).appendPoint([212.1679465,-138.73]).appendPoint([201.130009,-143.8770748]).appendArc([200.0506976,-144.727627],{"radius":3,"clockwise":false,"large":false}).appendArc([198.7348985,-145.1238905],{"radius":3,"clockwise":false,"large":false}).appendPoint([184.8784921,-153.1238905]).appendArc([183.7804159,-157.2219667],{"radius":3,"clockwise":false,"large":false}).appendPoint([191.7804159,-171.0783731]).appendArc([195.8784921,-172.1764493],{"radius":3,"clockwise":false,"large":false}).appendPoint([209.7348985,-164.1764493]).appendArc([210.0614963,-163.9581925],{"radius":3,"clockwise":false,"large":false}).appendArc([210.4276108,-163.8158462],{"radius":3,"clockwise":false,"large":false}).appendPoint([224.9285354,-157.053954]).appendArc([225.0819068,-156.9770215],{"radius":3,"clockwise":false,"large":false}).appendArc([225.2516679,-156.9520707],{"radius":3,"clockwise":false,"large":false}).appendPoint([241.008592,-154.1736999]).appendArc([243.4420707,-150.6983321],{"radius":3,"clockwise":false,"large":false}).appendPoint([240.7322192,-135.33]).appendPoint([245,-135.33]).appendArc([247.966058,-132.78],{"radius":3,"clockwise":false,"large":false}).appendPoint([260,-132.78]).appendPoint([260,-142.53]).appendArc([263,-145.53],{"radius":3,"clockwise":false,"large":false}).appendPoint([277,-145.53]).appendPoint([277,-153.75]).appendArc([280,-156.75],{"radius":3,"clockwise":false,"large":false}).appendPoint([296,-156.75]).appendArc([299,-153.75],{"radius":3,"clockwise":false,"large":false}).appendPoint([299,-144]).close().innerToCAG()
.extrude({ offset: [0, 0, 1] });
}




                function r_3d_preview_case_fn() {
                    

                // creating part 0 of case r_3d_preview
                let r_3d_preview__part_0 = r_case_bottom_extrude_3_outline_fn();

                // make sure that rotations are relative
                let r_3d_preview__part_0_bounds = r_3d_preview__part_0.getBounds();
                let r_3d_preview__part_0_x = r_3d_preview__part_0_bounds[0].x + (r_3d_preview__part_0_bounds[1].x - r_3d_preview__part_0_bounds[0].x) / 2
                let r_3d_preview__part_0_y = r_3d_preview__part_0_bounds[0].y + (r_3d_preview__part_0_bounds[1].y - r_3d_preview__part_0_bounds[0].y) / 2
                r_3d_preview__part_0 = translate([-r_3d_preview__part_0_x, -r_3d_preview__part_0_y, 0], r_3d_preview__part_0);
                r_3d_preview__part_0 = rotate([0,0,0], r_3d_preview__part_0);
                r_3d_preview__part_0 = translate([r_3d_preview__part_0_x, r_3d_preview__part_0_y, 0], r_3d_preview__part_0);

                r_3d_preview__part_0 = translate([0,0,0], r_3d_preview__part_0);
                let result = r_3d_preview__part_0;
                
            

                // creating part 1 of case r_3d_preview
                let r_3d_preview__part_1 = r_case_border_extrude_11_2_outline_fn();

                // make sure that rotations are relative
                let r_3d_preview__part_1_bounds = r_3d_preview__part_1.getBounds();
                let r_3d_preview__part_1_x = r_3d_preview__part_1_bounds[0].x + (r_3d_preview__part_1_bounds[1].x - r_3d_preview__part_1_bounds[0].x) / 2
                let r_3d_preview__part_1_y = r_3d_preview__part_1_bounds[0].y + (r_3d_preview__part_1_bounds[1].y - r_3d_preview__part_1_bounds[0].y) / 2
                r_3d_preview__part_1 = translate([-r_3d_preview__part_1_x, -r_3d_preview__part_1_y, 0], r_3d_preview__part_1);
                r_3d_preview__part_1 = rotate([0,0,0], r_3d_preview__part_1);
                r_3d_preview__part_1 = translate([r_3d_preview__part_1_x, r_3d_preview__part_1_y, 0], r_3d_preview__part_1);

                r_3d_preview__part_1 = translate([0,0,0], r_3d_preview__part_1);
                result = result.union(r_3d_preview__part_1);
                
            

                // creating part 2 of case r_3d_preview
                let r_3d_preview__part_2 = r_usbc_border_outline_extrude_8_2_outline_fn();

                // make sure that rotations are relative
                let r_3d_preview__part_2_bounds = r_3d_preview__part_2.getBounds();
                let r_3d_preview__part_2_x = r_3d_preview__part_2_bounds[0].x + (r_3d_preview__part_2_bounds[1].x - r_3d_preview__part_2_bounds[0].x) / 2
                let r_3d_preview__part_2_y = r_3d_preview__part_2_bounds[0].y + (r_3d_preview__part_2_bounds[1].y - r_3d_preview__part_2_bounds[0].y) / 2
                r_3d_preview__part_2 = translate([-r_3d_preview__part_2_x, -r_3d_preview__part_2_y, 0], r_3d_preview__part_2);
                r_3d_preview__part_2 = rotate([0,0,0], r_3d_preview__part_2);
                r_3d_preview__part_2 = translate([r_3d_preview__part_2_x, r_3d_preview__part_2_y, 0], r_3d_preview__part_2);

                r_3d_preview__part_2 = translate([20,5,3], r_3d_preview__part_2);
                result = result.subtract(r_3d_preview__part_2);
                
            

                // creating part 3 of case r_3d_preview
                let r_3d_preview__part_3 = r_coverpart_switch_plate_outline_extrude_3_outline_fn();

                // make sure that rotations are relative
                let r_3d_preview__part_3_bounds = r_3d_preview__part_3.getBounds();
                let r_3d_preview__part_3_x = r_3d_preview__part_3_bounds[0].x + (r_3d_preview__part_3_bounds[1].x - r_3d_preview__part_3_bounds[0].x) / 2
                let r_3d_preview__part_3_y = r_3d_preview__part_3_bounds[0].y + (r_3d_preview__part_3_bounds[1].y - r_3d_preview__part_3_bounds[0].y) / 2
                r_3d_preview__part_3 = translate([-r_3d_preview__part_3_x, -r_3d_preview__part_3_y, 0], r_3d_preview__part_3);
                r_3d_preview__part_3 = rotate([0,0,0], r_3d_preview__part_3);
                r_3d_preview__part_3 = translate([r_3d_preview__part_3_x, r_3d_preview__part_3_y, 0], r_3d_preview__part_3);

                r_3d_preview__part_3 = translate([0,0,25], r_3d_preview__part_3);
                result = result.union(r_3d_preview__part_3);
                
            

                // creating part 4 of case r_3d_preview
                let r_3d_preview__part_4 = r_pcb_outline_extrude_1_outline_fn();

                // make sure that rotations are relative
                let r_3d_preview__part_4_bounds = r_3d_preview__part_4.getBounds();
                let r_3d_preview__part_4_x = r_3d_preview__part_4_bounds[0].x + (r_3d_preview__part_4_bounds[1].x - r_3d_preview__part_4_bounds[0].x) / 2
                let r_3d_preview__part_4_y = r_3d_preview__part_4_bounds[0].y + (r_3d_preview__part_4_bounds[1].y - r_3d_preview__part_4_bounds[0].y) / 2
                r_3d_preview__part_4 = translate([-r_3d_preview__part_4_x, -r_3d_preview__part_4_y, 0], r_3d_preview__part_4);
                r_3d_preview__part_4 = rotate([0,0,0], r_3d_preview__part_4);
                r_3d_preview__part_4 = translate([r_3d_preview__part_4_x, r_3d_preview__part_4_y, 0], r_3d_preview__part_4);

                r_3d_preview__part_4 = translate([0,0,20], r_3d_preview__part_4);
                result = result.union(r_3d_preview__part_4);
                
            
                    return result;
                }
            
            
        
            function main() {
                return r_3d_preview_case_fn();
            }

        