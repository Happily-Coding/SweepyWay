function l_case_bottom_extrude_3_outline_fn(){
    return new CSG.Path2D([[27,-148],[37,-148]]).appendPoint([37,-153.75]).appendArc([44,-160.75],{"radius":7,"clockwise":false,"large":false}).appendPoint([60,-160.75]).appendArc([67,-153.75],{"radius":7,"clockwise":false,"large":false}).appendPoint([67,-149.53]).appendPoint([77,-149.53]).appendArc([84,-142.53],{"radius":7,"clockwise":false,"large":false}).appendPoint([84,-136.78]).appendPoint([89.5965289,-136.78]).appendArc([94.5038705,-139.3123961],{"radius":7,"clockwise":false,"large":false}).appendPoint([92.6186982,-150.0037394]).appendArc([98.2968154,-158.1129309],{"radius":7,"clockwise":false,"large":false}).appendArc([98.2968153,-158.1129309],{"radius":4,"clockwise":false,"large":false}).appendPoint([113.7034028,-160.8295279]).appendPoint([127.8811056,-167.4406993]).appendArc([128.0794093,-167.52948],{"radius":7,"clockwise":false,"large":false}).appendArc([128.2651015,-167.6405509],{"radius":7,"clockwise":false,"large":false}).appendPoint([142.1215079,-175.6405509]).appendArc([151.6836857,-173.0783731],{"radius":7,"clockwise":false,"large":false}).appendPoint([159.6836857,-159.2219667]).appendArc([157.1215079,-149.6597889],{"radius":7,"clockwise":false,"large":false}).appendPoint([143.2651015,-141.6597889]).appendArc([141.866452,-141.0448171],{"radius":7,"clockwise":false,"large":false}).appendArc([140.560464,-140.2518437],{"radius":7,"clockwise":false,"large":false}).appendPoint([138.5835638,-139.33]).appendPoint([145,-139.33]).appendArc([152,-132.33],{"radius":7,"clockwise":false,"large":false}).appendPoint([152,-116.33]).appendArc([151.98212,-115.83],{"radius":7,"clockwise":false,"large":false}).appendArc([152,-115.33],{"radius":7,"clockwise":false,"large":false}).appendPoint([152,-99.33]).appendArc([151.98212,-98.83],{"radius":7,"clockwise":false,"large":false}).appendArc([152,-98.33],{"radius":7,"clockwise":false,"large":false}).appendPoint([152,-82.33]).appendArc([145,-75.33],{"radius":7,"clockwise":false,"large":false}).appendPoint([135,-75.33]).appendPoint([135,-68.73]).appendArc([128,-61.73],{"radius":7,"clockwise":false,"large":false}).appendPoint([122,-61.73]).appendPoint([122,-55.77]).appendArc([118.75,-49.8592048],{"radius":7,"clockwise":false,"large":false}).appendPoint([118.75,-40.77]).appendArc([111.75,-33.77],{"radius":7,"clockwise":false,"large":false}).appendPoint([67.75,-33.77]).appendArc([60.75,-40.77],{"radius":7,"clockwise":false,"large":false}).appendPoint([60.75,-51.5344657]).appendArc([54,-58.53],{"radius":7,"clockwise":false,"large":false}).appendPoint([54,-62.75]).appendPoint([44,-62.75]).appendArc([37.5628034,-67],{"radius":7,"clockwise":false,"large":false}).appendPoint([27,-67]).appendArc([20,-74],{"radius":7,"clockwise":false,"large":false}).appendPoint([20,-90]).appendArc([20.01788,-90.5],{"radius":7,"clockwise":false,"large":false}).appendArc([20,-91],{"radius":7,"clockwise":false,"large":false}).appendPoint([20,-107]).appendArc([20.01788,-107.5],{"radius":7,"clockwise":false,"large":false}).appendArc([20,-108],{"radius":7,"clockwise":false,"large":false}).appendPoint([20,-124]).appendArc([20.01788,-124.5],{"radius":7,"clockwise":false,"large":false}).appendArc([20,-125],{"radius":7,"clockwise":false,"large":false}).appendPoint([20,-141]).appendArc([27,-148],{"radius":7,"clockwise":false,"large":false}).close().innerToCAG()
.subtract(
    CAG.circle({"center":[131.7104269,-160.2956003],"radius":1.1})
.union(
    CAG.circle({"center":[128.8,-132.63],"radius":1.1})
).union(
    CAG.circle({"center":[128.8,-80.13],"radius":1.1})
).union(
    CAG.circle({"center":[43.8,-137.15],"radius":1.1})
).union(
    CAG.circle({"center":[43.8,-86.15],"radius":1.1})
)).extrude({ offset: [0, 0, 3] });
}


function l_case_border_extrude_11_2_outline_fn(){
    return new CSG.Path2D([[27,-148],[37,-148]]).appendPoint([37,-153.75]).appendArc([44,-160.75],{"radius":7,"clockwise":false,"large":false}).appendPoint([60,-160.75]).appendArc([67,-153.75],{"radius":7,"clockwise":false,"large":false}).appendPoint([67,-149.53]).appendPoint([77,-149.53]).appendArc([84,-142.53],{"radius":7,"clockwise":false,"large":false}).appendPoint([84,-136.78]).appendPoint([89.5965289,-136.78]).appendArc([94.5038705,-139.3123961],{"radius":7,"clockwise":false,"large":false}).appendPoint([92.6186982,-150.0037394]).appendArc([98.2968154,-158.1129309],{"radius":7,"clockwise":false,"large":false}).appendArc([98.2968153,-158.1129309],{"radius":4,"clockwise":false,"large":false}).appendPoint([113.7034028,-160.8295279]).appendPoint([127.8811056,-167.4406993]).appendArc([128.0794093,-167.52948],{"radius":7,"clockwise":false,"large":false}).appendArc([128.2651015,-167.6405509],{"radius":7,"clockwise":false,"large":false}).appendPoint([142.1215079,-175.6405509]).appendArc([151.6836857,-173.0783731],{"radius":7,"clockwise":false,"large":false}).appendPoint([159.6836857,-159.2219667]).appendArc([157.1215079,-149.6597889],{"radius":7,"clockwise":false,"large":false}).appendPoint([143.2651015,-141.6597889]).appendArc([141.866452,-141.0448171],{"radius":7,"clockwise":false,"large":false}).appendArc([140.560464,-140.2518437],{"radius":7,"clockwise":false,"large":false}).appendPoint([138.5835638,-139.33]).appendPoint([145,-139.33]).appendArc([152,-132.33],{"radius":7,"clockwise":false,"large":false}).appendPoint([152,-116.33]).appendArc([151.98212,-115.83],{"radius":7,"clockwise":false,"large":false}).appendArc([152,-115.33],{"radius":7,"clockwise":false,"large":false}).appendPoint([152,-99.33]).appendArc([151.98212,-98.83],{"radius":7,"clockwise":false,"large":false}).appendArc([152,-98.33],{"radius":7,"clockwise":false,"large":false}).appendPoint([152,-82.33]).appendArc([145,-75.33],{"radius":7,"clockwise":false,"large":false}).appendPoint([135,-75.33]).appendPoint([135,-68.73]).appendArc([128,-61.73],{"radius":7,"clockwise":false,"large":false}).appendPoint([122,-61.73]).appendPoint([122,-55.77]).appendArc([118.75,-49.8592048],{"radius":7,"clockwise":false,"large":false}).appendPoint([118.75,-40.77]).appendArc([111.75,-33.77],{"radius":7,"clockwise":false,"large":false}).appendPoint([67.75,-33.77]).appendArc([60.75,-40.77],{"radius":7,"clockwise":false,"large":false}).appendPoint([60.75,-51.5344657]).appendArc([54,-58.53],{"radius":7,"clockwise":false,"large":false}).appendPoint([54,-62.75]).appendPoint([44,-62.75]).appendArc([37.5628034,-67],{"radius":7,"clockwise":false,"large":false}).appendPoint([27,-67]).appendArc([20,-74],{"radius":7,"clockwise":false,"large":false}).appendPoint([20,-90]).appendArc([20.01788,-90.5],{"radius":7,"clockwise":false,"large":false}).appendArc([20,-91],{"radius":7,"clockwise":false,"large":false}).appendPoint([20,-107]).appendArc([20.01788,-107.5],{"radius":7,"clockwise":false,"large":false}).appendArc([20,-108],{"radius":7,"clockwise":false,"large":false}).appendPoint([20,-124]).appendArc([20.01788,-124.5],{"radius":7,"clockwise":false,"large":false}).appendArc([20,-125],{"radius":7,"clockwise":false,"large":false}).appendPoint([20,-141]).appendArc([27,-148],{"radius":7,"clockwise":false,"large":false}).close().innerToCAG()
.subtract(
    new CSG.Path2D([[27,-146],[39,-146]]).appendPoint([39,-153.75]).appendArc([44,-158.75],{"radius":5,"clockwise":false,"large":false}).appendPoint([60,-158.75]).appendArc([65,-153.75],{"radius":5,"clockwise":false,"large":false}).appendPoint([65,-147.53]).appendPoint([77,-147.53]).appendArc([82,-142.53],{"radius":5,"clockwise":false,"large":false}).appendPoint([82,-134.78]).appendPoint([90.6413878,-134.78]).appendArc([95,-137.33],{"radius":5,"clockwise":false,"large":false}).appendPoint([96.8842737,-137.33]).appendPoint([94.5883137,-150.3510358]).appendArc([98.6433075,-156.1431735],{"radius":5,"clockwise":false,"large":false}).appendPoint([114.3100036,-158.9056348]).appendPoint([128.7271527,-165.6284618]).appendArc([129.0065139,-165.7485283],{"radius":5,"clockwise":false,"large":false}).appendArc([129.2651015,-165.9085001],{"radius":5,"clockwise":false,"large":false}).appendPoint([143.1215079,-173.9085001]).appendArc([149.9516349,-172.0783731],{"radius":5,"clockwise":false,"large":false}).appendPoint([157.9516349,-158.2219667]).appendArc([156.1215079,-151.3918397],{"radius":5,"clockwise":false,"large":false}).appendPoint([142.2651015,-143.3918397]).appendArc([140.9226686,-142.8578081],{"radius":5,"clockwise":false,"large":false}).appendArc([139.7152275,-142.0644593],{"radius":5,"clockwise":false,"large":false}).appendPoint([132.1408068,-138.5324488]).appendArc([132.7370877,-137.33],{"radius":5,"clockwise":false,"large":false}).appendPoint([145,-137.33]).appendArc([150,-132.33],{"radius":5,"clockwise":false,"large":false}).appendPoint([150,-116.33]).appendArc([149.9749372,-115.83],{"radius":5,"clockwise":false,"large":false}).appendArc([150,-115.33],{"radius":5,"clockwise":false,"large":false}).appendPoint([150,-99.33]).appendArc([149.9749372,-98.83],{"radius":5,"clockwise":false,"large":false}).appendArc([150,-98.33],{"radius":5,"clockwise":false,"large":false}).appendPoint([150,-82.33]).appendArc([145,-77.33],{"radius":5,"clockwise":false,"large":false}).appendPoint([133,-77.33]).appendPoint([133,-68.73]).appendArc([128,-63.73],{"radius":5,"clockwise":false,"large":false}).appendPoint([120,-63.73]).appendPoint([120,-55.77]).appendArc([116.75,-51.0862515],{"radius":5,"clockwise":false,"large":false}).appendPoint([116.75,-40.77]).appendArc([111.75,-35.77],{"radius":5,"clockwise":false,"large":false}).appendPoint([67.75,-35.77]).appendArc([62.75,-40.77],{"radius":5,"clockwise":false,"large":false}).appendPoint([62.75,-53.53]).appendPoint([61,-53.53]).appendArc([56,-58.53],{"radius":5,"clockwise":false,"large":false}).appendPoint([56,-64.75]).appendPoint([44,-64.75]).appendArc([39.05657,-69],{"radius":5,"clockwise":false,"large":false}).appendPoint([27,-69]).appendArc([22,-74],{"radius":5,"clockwise":false,"large":false}).appendPoint([22,-90]).appendArc([22.0250628,-90.5],{"radius":5,"clockwise":false,"large":false}).appendArc([22,-91],{"radius":5,"clockwise":false,"large":false}).appendPoint([22,-107]).appendArc([22.0250628,-107.5],{"radius":5,"clockwise":false,"large":false}).appendArc([22,-108],{"radius":5,"clockwise":false,"large":false}).appendPoint([22,-124]).appendArc([22.0250628,-124.5],{"radius":5,"clockwise":false,"large":false}).appendArc([22,-125],{"radius":5,"clockwise":false,"large":false}).appendPoint([22,-141]).appendArc([27,-146],{"radius":5,"clockwise":false,"large":false}).close().innerToCAG()
).extrude({ offset: [0, 0, 11.2] });
}


function l_usbc_border_outline_extrude_7_199999999999999_outline_fn(){
    return new CSG.Path2D([[74.25,-55.27],[89.25,-55.27]]).appendPoint([89.25,-40.27]).appendPoint([74.25,-40.27]).appendPoint([74.25,-55.27]).close().innerToCAG()
.extrude({ offset: [0, 0, 7.199999999999999] });
}


function l_coverpart_switch_plate_outline_extrude_3_outline_fn(){
    return new CSG.Path2D([[27,-144],[41,-144]]).appendPoint([41,-153.75]).appendArc([44,-156.75],{"radius":3,"clockwise":false,"large":false}).appendPoint([60,-156.75]).appendArc([63,-153.75],{"radius":3,"clockwise":false,"large":false}).appendPoint([63,-145.53]).appendPoint([77,-145.53]).appendArc([80,-142.53],{"radius":3,"clockwise":false,"large":false}).appendPoint([80,-132.78]).appendPoint([92.033942,-132.78]).appendArc([95,-135.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([99.2677808,-135.33]).appendPoint([96.5579293,-150.6983321]).appendArc([98.9914081,-154.1736999],{"radius":3,"clockwise":false,"large":false}).appendPoint([114.7483321,-156.9520707]).appendArc([114.9180932,-156.9770215],{"radius":3,"clockwise":false,"large":false}).appendArc([115.0714646,-157.053954],{"radius":3,"clockwise":false,"large":false}).appendPoint([129.5723892,-163.8158462]).appendArc([129.9385037,-163.9581925],{"radius":3,"clockwise":false,"large":false}).appendArc([130.2651015,-164.1764493],{"radius":3,"clockwise":false,"large":false}).appendPoint([144.1215079,-172.1764493]).appendArc([148.2195841,-171.0783731],{"radius":3,"clockwise":false,"large":false}).appendPoint([156.2195841,-157.2219667]).appendArc([155.1215079,-153.1238905],{"radius":3,"clockwise":false,"large":false}).appendPoint([141.2651015,-145.1238905]).appendArc([139.9493024,-144.727627],{"radius":3,"clockwise":false,"large":false}).appendArc([138.869991,-143.8770748],{"radius":3,"clockwise":false,"large":false}).appendPoint([127.8320535,-138.73]).appendPoint([128,-138.73]).appendArc([131,-135.73],{"radius":3,"clockwise":false,"large":false}).appendPoint([131,-135.33]).appendPoint([145,-135.33]).appendArc([148,-132.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([148,-116.33]).appendArc([147.9580399,-115.83],{"radius":3,"clockwise":false,"large":false}).appendArc([148,-115.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([148,-99.33]).appendArc([147.9580399,-98.83],{"radius":3,"clockwise":false,"large":false}).appendArc([148,-98.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([148,-82.33]).appendArc([145,-79.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([131,-79.33]).appendPoint([131,-68.73]).appendArc([128,-65.73],{"radius":3,"clockwise":false,"large":false}).appendPoint([114,-65.73]).appendPoint([114,-65.33]).appendArc([111,-62.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([96.966058,-62.33]).appendArc([94,-59.78],{"radius":3,"clockwise":false,"large":false}).appendPoint([80,-59.78]).appendPoint([80,-58.53]).appendArc([77,-55.53],{"radius":3,"clockwise":false,"large":false}).appendPoint([61,-55.53]).appendArc([58,-58.53],{"radius":3,"clockwise":false,"large":false}).appendPoint([58,-66.75]).appendPoint([44,-66.75]).appendArc([41,-69.75],{"radius":3,"clockwise":false,"large":false}).appendPoint([41,-71]).appendPoint([27,-71]).appendArc([24,-74],{"radius":3,"clockwise":false,"large":false}).appendPoint([24,-90]).appendArc([24.0419601,-90.5],{"radius":3,"clockwise":false,"large":false}).appendArc([24,-91],{"radius":3,"clockwise":false,"large":false}).appendPoint([24,-107]).appendArc([24.0419601,-107.5],{"radius":3,"clockwise":false,"large":false}).appendArc([24,-108],{"radius":3,"clockwise":false,"large":false}).appendPoint([24,-124]).appendArc([24.0419601,-124.5],{"radius":3,"clockwise":false,"large":false}).appendArc([24,-125],{"radius":3,"clockwise":false,"large":false}).appendPoint([24,-141]).appendArc([27,-144],{"radius":3,"clockwise":false,"large":false}).close().innerToCAG()
.subtract(
    CAG.circle({"center":[131.7104269,-160.2956003],"radius":1.1})
.union(
    CAG.circle({"center":[128.8,-132.63],"radius":1.1})
).union(
    CAG.circle({"center":[128.8,-80.13],"radius":1.1})
).union(
    CAG.circle({"center":[43.8,-137.15],"radius":1.1})
).union(
    CAG.circle({"center":[43.8,-86.15],"radius":1.1})
).union(
    new CSG.Path2D([[133.1311269,-161.2123477],[145.2554825,-168.2123477]]).appendPoint([152.2554825,-156.0879921]).appendPoint([140.1311269,-149.0879921]).appendPoint([133.1311269,-161.2123477]).close().innerToCAG()
).union(
    new CSG.Path2D([[117.6682455,-153.8513411],[130.3565545,-159.7679967]]).appendPoint([136.2732101,-147.0796877]).appendPoint([123.5849011,-141.1630321]).appendPoint([117.6682455,-153.8513411]).close().innerToCAG()
).union(
    new CSG.Path2D([[100.6708085,-150.408117],[114.458117,-152.8391915]]).appendPoint([116.8891915,-139.051883]).appendPoint([103.101883,-136.6208085]).appendPoint([100.6708085,-150.408117]).close().innerToCAG()
).union(
    new CSG.Path2D([[130,-97.33],[144,-97.33]]).appendPoint([144,-83.33]).appendPoint([130,-83.33]).appendPoint([130,-97.33]).close().innerToCAG()
).union(
    new CSG.Path2D([[130,-114.33],[144,-114.33]]).appendPoint([144,-100.33]).appendPoint([130,-100.33]).appendPoint([130,-114.33]).close().innerToCAG()
).union(
    new CSG.Path2D([[130,-131.33],[144,-131.33]]).appendPoint([144,-117.33]).appendPoint([130,-117.33]).appendPoint([130,-131.33]).close().innerToCAG()
).union(
    new CSG.Path2D([[113,-83.73],[127,-83.73]]).appendPoint([127,-69.73]).appendPoint([113,-69.73]).appendPoint([113,-83.73]).close().innerToCAG()
).union(
    new CSG.Path2D([[113,-100.73],[127,-100.73]]).appendPoint([127,-86.73]).appendPoint([113,-86.73]).appendPoint([113,-100.73]).close().innerToCAG()
).union(
    new CSG.Path2D([[113,-117.73],[127,-117.73]]).appendPoint([127,-103.73]).appendPoint([113,-103.73]).appendPoint([113,-117.73]).close().innerToCAG()
).union(
    new CSG.Path2D([[113,-134.73],[127,-134.73]]).appendPoint([127,-120.73]).appendPoint([113,-120.73]).appendPoint([113,-134.73]).close().innerToCAG()
).union(
    new CSG.Path2D([[96,-80.33],[110,-80.33]]).appendPoint([110,-66.33]).appendPoint([96,-66.33]).appendPoint([96,-80.33]).close().innerToCAG()
).union(
    new CSG.Path2D([[96,-97.33],[110,-97.33]]).appendPoint([110,-83.33]).appendPoint([96,-83.33]).appendPoint([96,-97.33]).close().innerToCAG()
).union(
    new CSG.Path2D([[96,-114.33],[110,-114.33]]).appendPoint([110,-100.33]).appendPoint([96,-100.33]).appendPoint([96,-114.33]).close().innerToCAG()
).union(
    new CSG.Path2D([[96,-131.33],[110,-131.33]]).appendPoint([110,-117.33]).appendPoint([96,-117.33]).appendPoint([96,-131.33]).close().innerToCAG()
).union(
    new CSG.Path2D([[79,-77.78],[93,-77.78]]).appendPoint([93,-63.78]).appendPoint([79,-63.78]).appendPoint([79,-77.78]).close().innerToCAG()
).union(
    new CSG.Path2D([[79,-94.78],[93,-94.78]]).appendPoint([93,-80.78]).appendPoint([79,-80.78]).appendPoint([79,-94.78]).close().innerToCAG()
).union(
    new CSG.Path2D([[79,-111.78],[93,-111.78]]).appendPoint([93,-97.78]).appendPoint([79,-97.78]).appendPoint([79,-111.78]).close().innerToCAG()
).union(
    new CSG.Path2D([[79,-128.78],[93,-128.78]]).appendPoint([93,-114.78]).appendPoint([79,-114.78]).appendPoint([79,-128.78]).close().innerToCAG()
).union(
    new CSG.Path2D([[62,-73.53],[76,-73.53]]).appendPoint([76,-59.53]).appendPoint([62,-59.53]).appendPoint([62,-73.53]).close().innerToCAG()
).union(
    new CSG.Path2D([[62,-90.53],[76,-90.53]]).appendPoint([76,-76.53]).appendPoint([62,-76.53]).appendPoint([62,-90.53]).close().innerToCAG()
).union(
    new CSG.Path2D([[62,-107.53],[76,-107.53]]).appendPoint([76,-93.53]).appendPoint([62,-93.53]).appendPoint([62,-107.53]).close().innerToCAG()
).union(
    new CSG.Path2D([[62,-124.53],[76,-124.53]]).appendPoint([76,-110.53]).appendPoint([62,-110.53]).appendPoint([62,-124.53]).close().innerToCAG()
).union(
    new CSG.Path2D([[62,-141.53],[76,-141.53]]).appendPoint([76,-127.53]).appendPoint([62,-127.53]).appendPoint([62,-141.53]).close().innerToCAG()
).union(
    new CSG.Path2D([[45,-84.75],[59,-84.75]]).appendPoint([59,-70.75]).appendPoint([45,-70.75]).appendPoint([45,-84.75]).close().innerToCAG()
).union(
    new CSG.Path2D([[45,-101.75],[59,-101.75]]).appendPoint([59,-87.75]).appendPoint([45,-87.75]).appendPoint([45,-101.75]).close().innerToCAG()
).union(
    new CSG.Path2D([[45,-118.75],[59,-118.75]]).appendPoint([59,-104.75]).appendPoint([45,-104.75]).appendPoint([45,-118.75]).close().innerToCAG()
).union(
    new CSG.Path2D([[45,-135.75],[59,-135.75]]).appendPoint([59,-121.75]).appendPoint([45,-121.75]).appendPoint([45,-135.75]).close().innerToCAG()
).union(
    new CSG.Path2D([[45,-152.75],[59,-152.75]]).appendPoint([59,-138.75]).appendPoint([45,-138.75]).appendPoint([45,-152.75]).close().innerToCAG()
).union(
    new CSG.Path2D([[28,-89],[42,-89]]).appendPoint([42,-75]).appendPoint([28,-75]).appendPoint([28,-89]).close().innerToCAG()
).union(
    new CSG.Path2D([[28,-106],[42,-106]]).appendPoint([42,-92]).appendPoint([28,-92]).appendPoint([28,-106]).close().innerToCAG()
).union(
    new CSG.Path2D([[28,-123],[42,-123]]).appendPoint([42,-109]).appendPoint([28,-109]).appendPoint([28,-123]).close().innerToCAG()
).union(
    new CSG.Path2D([[28,-140],[42,-140]]).appendPoint([42,-126]).appendPoint([28,-126]).appendPoint([28,-140]).close().innerToCAG()
)).extrude({ offset: [0, 0, 3] });
}


function l_pcb_outline_extrude_1_outline_fn(){
    return new CSG.Path2D([[27,-144],[41,-144]]).appendPoint([41,-153.75]).appendArc([44,-156.75],{"radius":3,"clockwise":false,"large":false}).appendPoint([60,-156.75]).appendArc([63,-153.75],{"radius":3,"clockwise":false,"large":false}).appendPoint([63,-145.53]).appendPoint([77,-145.53]).appendArc([80,-142.53],{"radius":3,"clockwise":false,"large":false}).appendPoint([80,-132.78]).appendPoint([92.033942,-132.78]).appendArc([95,-135.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([99.2677808,-135.33]).appendPoint([96.5579293,-150.6983321]).appendArc([98.9914081,-154.1736999],{"radius":3,"clockwise":false,"large":false}).appendPoint([114.7483321,-156.9520707]).appendArc([114.9180932,-156.9770215],{"radius":3,"clockwise":false,"large":false}).appendArc([115.0714646,-157.053954],{"radius":3,"clockwise":false,"large":false}).appendPoint([129.5723892,-163.8158462]).appendArc([129.9385037,-163.9581925],{"radius":3,"clockwise":false,"large":false}).appendArc([130.2651015,-164.1764493],{"radius":3,"clockwise":false,"large":false}).appendPoint([144.1215079,-172.1764493]).appendArc([148.2195841,-171.0783731],{"radius":3,"clockwise":false,"large":false}).appendPoint([156.2195841,-157.2219667]).appendArc([155.1215079,-153.1238905],{"radius":3,"clockwise":false,"large":false}).appendPoint([141.2651015,-145.1238905]).appendArc([139.9493024,-144.727627],{"radius":3,"clockwise":false,"large":false}).appendArc([138.869991,-143.8770748],{"radius":3,"clockwise":false,"large":false}).appendPoint([127.8320535,-138.73]).appendPoint([128,-138.73]).appendArc([131,-135.73],{"radius":3,"clockwise":false,"large":false}).appendPoint([131,-135.33]).appendPoint([145,-135.33]).appendArc([148,-132.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([148,-116.33]).appendArc([147.9580399,-115.83],{"radius":3,"clockwise":false,"large":false}).appendArc([148,-115.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([148,-99.33]).appendArc([147.9580399,-98.83],{"radius":3,"clockwise":false,"large":false}).appendArc([148,-98.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([148,-82.33]).appendArc([145,-79.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([131,-79.33]).appendPoint([131,-68.73]).appendArc([128,-65.73],{"radius":3,"clockwise":false,"large":false}).appendPoint([118,-65.73]).appendPoint([118,-55.77]).appendArc([115,-52.77],{"radius":3,"clockwise":false,"large":false}).appendPoint([114.75,-52.77]).appendPoint([114.75,-40.77]).appendArc([111.75,-37.77],{"radius":3,"clockwise":false,"large":false}).appendPoint([67.75,-37.77]).appendArc([64.75,-40.77],{"radius":3,"clockwise":false,"large":false}).appendPoint([64.75,-55.53]).appendPoint([61,-55.53]).appendArc([58,-58.53],{"radius":3,"clockwise":false,"large":false}).appendPoint([58,-66.75]).appendPoint([44,-66.75]).appendArc([41,-69.75],{"radius":3,"clockwise":false,"large":false}).appendPoint([41,-71]).appendPoint([27,-71]).appendArc([24,-74],{"radius":3,"clockwise":false,"large":false}).appendPoint([24,-90]).appendArc([24.0419601,-90.5],{"radius":3,"clockwise":false,"large":false}).appendArc([24,-91],{"radius":3,"clockwise":false,"large":false}).appendPoint([24,-107]).appendArc([24.0419601,-107.5],{"radius":3,"clockwise":false,"large":false}).appendArc([24,-108],{"radius":3,"clockwise":false,"large":false}).appendPoint([24,-124]).appendArc([24.0419601,-124.5],{"radius":3,"clockwise":false,"large":false}).appendArc([24,-125],{"radius":3,"clockwise":false,"large":false}).appendPoint([24,-141]).appendArc([27,-144],{"radius":3,"clockwise":false,"large":false}).close().innerToCAG()
.extrude({ offset: [0, 0, 1] });
}




                function l_3d_preview_case_fn() {
                    

                // creating part 0 of case l_3d_preview
                let l_3d_preview__part_0 = l_case_bottom_extrude_3_outline_fn();

                // make sure that rotations are relative
                let l_3d_preview__part_0_bounds = l_3d_preview__part_0.getBounds();
                let l_3d_preview__part_0_x = l_3d_preview__part_0_bounds[0].x + (l_3d_preview__part_0_bounds[1].x - l_3d_preview__part_0_bounds[0].x) / 2
                let l_3d_preview__part_0_y = l_3d_preview__part_0_bounds[0].y + (l_3d_preview__part_0_bounds[1].y - l_3d_preview__part_0_bounds[0].y) / 2
                l_3d_preview__part_0 = translate([-l_3d_preview__part_0_x, -l_3d_preview__part_0_y, 0], l_3d_preview__part_0);
                l_3d_preview__part_0 = rotate([0,0,0], l_3d_preview__part_0);
                l_3d_preview__part_0 = translate([l_3d_preview__part_0_x, l_3d_preview__part_0_y, 0], l_3d_preview__part_0);

                l_3d_preview__part_0 = translate([0,0,0], l_3d_preview__part_0);
                let result = l_3d_preview__part_0;
                
            

                // creating part 1 of case l_3d_preview
                let l_3d_preview__part_1 = l_case_border_extrude_11_2_outline_fn();

                // make sure that rotations are relative
                let l_3d_preview__part_1_bounds = l_3d_preview__part_1.getBounds();
                let l_3d_preview__part_1_x = l_3d_preview__part_1_bounds[0].x + (l_3d_preview__part_1_bounds[1].x - l_3d_preview__part_1_bounds[0].x) / 2
                let l_3d_preview__part_1_y = l_3d_preview__part_1_bounds[0].y + (l_3d_preview__part_1_bounds[1].y - l_3d_preview__part_1_bounds[0].y) / 2
                l_3d_preview__part_1 = translate([-l_3d_preview__part_1_x, -l_3d_preview__part_1_y, 0], l_3d_preview__part_1);
                l_3d_preview__part_1 = rotate([0,0,0], l_3d_preview__part_1);
                l_3d_preview__part_1 = translate([l_3d_preview__part_1_x, l_3d_preview__part_1_y, 0], l_3d_preview__part_1);

                l_3d_preview__part_1 = translate([0,0,0], l_3d_preview__part_1);
                result = result.union(l_3d_preview__part_1);
                
            

                // creating part 2 of case l_3d_preview
                let l_3d_preview__part_2 = l_usbc_border_outline_extrude_7_199999999999999_outline_fn();

                // make sure that rotations are relative
                let l_3d_preview__part_2_bounds = l_3d_preview__part_2.getBounds();
                let l_3d_preview__part_2_x = l_3d_preview__part_2_bounds[0].x + (l_3d_preview__part_2_bounds[1].x - l_3d_preview__part_2_bounds[0].x) / 2
                let l_3d_preview__part_2_y = l_3d_preview__part_2_bounds[0].y + (l_3d_preview__part_2_bounds[1].y - l_3d_preview__part_2_bounds[0].y) / 2
                l_3d_preview__part_2 = translate([-l_3d_preview__part_2_x, -l_3d_preview__part_2_y, 0], l_3d_preview__part_2);
                l_3d_preview__part_2 = rotate([0,0,0], l_3d_preview__part_2);
                l_3d_preview__part_2 = translate([l_3d_preview__part_2_x, l_3d_preview__part_2_y, 0], l_3d_preview__part_2);

                l_3d_preview__part_2 = translate([0,7,3], l_3d_preview__part_2);
                result = result.subtract(l_3d_preview__part_2);
                
            

                // creating part 3 of case l_3d_preview
                let l_3d_preview__part_3 = l_coverpart_switch_plate_outline_extrude_3_outline_fn();

                // make sure that rotations are relative
                let l_3d_preview__part_3_bounds = l_3d_preview__part_3.getBounds();
                let l_3d_preview__part_3_x = l_3d_preview__part_3_bounds[0].x + (l_3d_preview__part_3_bounds[1].x - l_3d_preview__part_3_bounds[0].x) / 2
                let l_3d_preview__part_3_y = l_3d_preview__part_3_bounds[0].y + (l_3d_preview__part_3_bounds[1].y - l_3d_preview__part_3_bounds[0].y) / 2
                l_3d_preview__part_3 = translate([-l_3d_preview__part_3_x, -l_3d_preview__part_3_y, 0], l_3d_preview__part_3);
                l_3d_preview__part_3 = rotate([0,0,0], l_3d_preview__part_3);
                l_3d_preview__part_3 = translate([l_3d_preview__part_3_x, l_3d_preview__part_3_y, 0], l_3d_preview__part_3);

                l_3d_preview__part_3 = translate([0,0,25], l_3d_preview__part_3);
                result = result.union(l_3d_preview__part_3);
                
            

                // creating part 4 of case l_3d_preview
                let l_3d_preview__part_4 = l_pcb_outline_extrude_1_outline_fn();

                // make sure that rotations are relative
                let l_3d_preview__part_4_bounds = l_3d_preview__part_4.getBounds();
                let l_3d_preview__part_4_x = l_3d_preview__part_4_bounds[0].x + (l_3d_preview__part_4_bounds[1].x - l_3d_preview__part_4_bounds[0].x) / 2
                let l_3d_preview__part_4_y = l_3d_preview__part_4_bounds[0].y + (l_3d_preview__part_4_bounds[1].y - l_3d_preview__part_4_bounds[0].y) / 2
                l_3d_preview__part_4 = translate([-l_3d_preview__part_4_x, -l_3d_preview__part_4_y, 0], l_3d_preview__part_4);
                l_3d_preview__part_4 = rotate([0,0,0], l_3d_preview__part_4);
                l_3d_preview__part_4 = translate([l_3d_preview__part_4_x, l_3d_preview__part_4_y, 0], l_3d_preview__part_4);

                l_3d_preview__part_4 = translate([0,0,20], l_3d_preview__part_4);
                result = result.union(l_3d_preview__part_4);
                
            
                    return result;
                }
            
            
        
            function main() {
                return l_3d_preview_case_fn();
            }

        