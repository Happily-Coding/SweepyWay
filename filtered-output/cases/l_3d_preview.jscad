function l_case_bottom_extrude_3_outline_fn(){
    return new CSG.Path2D([[27,-148],[37,-148]]).appendPoint([37,-153.75]).appendArc([44,-160.75],{"radius":7,"clockwise":false,"large":false}).appendPoint([60,-160.75]).appendArc([67,-153.75],{"radius":7,"clockwise":false,"large":false}).appendPoint([67,-149.53]).appendPoint([77,-149.53]).appendArc([84,-142.53],{"radius":7,"clockwise":false,"large":false}).appendPoint([84,-136.78]).appendPoint([89.5965289,-136.78]).appendArc([94.5038705,-139.3123961],{"radius":7,"clockwise":false,"large":false}).appendPoint([92.6186982,-150.0037394]).appendArc([98.2968154,-158.1129309],{"radius":7,"clockwise":false,"large":false}).appendArc([98.2968153,-158.1129309],{"radius":4,"clockwise":false,"large":false}).appendPoint([113.7034028,-160.8295279]).appendPoint([127.8811056,-167.4406993]).appendArc([128.0794093,-167.52948],{"radius":7,"clockwise":false,"large":false}).appendArc([128.2651015,-167.6405509],{"radius":7,"clockwise":false,"large":false}).appendPoint([142.1215079,-175.6405509]).appendArc([151.6836857,-173.0783731],{"radius":7,"clockwise":false,"large":false}).appendPoint([159.6836857,-159.2219667]).appendArc([157.1215079,-149.6597889],{"radius":7,"clockwise":false,"large":false}).appendPoint([143.2651015,-141.6597889]).appendArc([141.866452,-141.0448171],{"radius":7,"clockwise":false,"large":false}).appendArc([140.560464,-140.2518437],{"radius":7,"clockwise":false,"large":false}).appendPoint([138.5835638,-139.33]).appendPoint([145,-139.33]).appendArc([152,-132.33],{"radius":7,"clockwise":false,"large":false}).appendPoint([152,-116.33]).appendArc([151.98212,-115.83],{"radius":7,"clockwise":false,"large":false}).appendArc([152,-115.33],{"radius":7,"clockwise":false,"large":false}).appendPoint([152,-99.33]).appendArc([151.98212,-98.83],{"radius":7,"clockwise":false,"large":false}).appendArc([152,-98.33],{"radius":7,"clockwise":false,"large":false}).appendPoint([152,-82.33]).appendArc([145,-75.33],{"radius":7,"clockwise":false,"large":false}).appendPoint([135,-75.33]).appendPoint([135,-68.73]).appendArc([128,-61.73],{"radius":7,"clockwise":false,"large":false}).appendPoint([122,-61.73]).appendPoint([122,-55.77]).appendArc([118.75,-49.8592048],{"radius":7,"clockwise":false,"large":false}).appendPoint([118.75,-40.77]).appendArc([111.75,-33.77],{"radius":7,"clockwise":false,"large":false}).appendPoint([67.75,-33.77]).appendArc([60.75,-40.77],{"radius":7,"clockwise":false,"large":false}).appendPoint([60.75,-51.5344657]).appendArc([54,-58.53],{"radius":7,"clockwise":false,"large":false}).appendPoint([54,-62.75]).appendPoint([44,-62.75]).appendArc([37.5628034,-67],{"radius":7,"clockwise":false,"large":false}).appendPoint([27,-67]).appendArc([20,-74],{"radius":7,"clockwise":false,"large":false}).appendPoint([20,-90]).appendArc([20.01788,-90.5],{"radius":7,"clockwise":false,"large":false}).appendArc([20,-91],{"radius":7,"clockwise":false,"large":false}).appendPoint([20,-107]).appendArc([20.01788,-107.5],{"radius":7,"clockwise":false,"large":false}).appendArc([20,-108],{"radius":7,"clockwise":false,"large":false}).appendPoint([20,-124]).appendArc([20.01788,-124.5],{"radius":7,"clockwise":false,"large":false}).appendArc([20,-125],{"radius":7,"clockwise":false,"large":false}).appendPoint([20,-141]).appendArc([27,-148],{"radius":7,"clockwise":false,"large":false}).close().innerToCAG()
.subtract(
    CAG.circle({"center":[119.0636178,-153.3434671],"radius":1.1})
.union(
    CAG.circle({"center":[114.05,-133.68],"radius":1.1})
).union(
    CAG.circle({"center":[114.05,-82.68],"radius":1.1})
).union(
    CAG.circle({"center":[29.05,-138.95],"radius":1.1})
).union(
    CAG.circle({"center":[29.05,-87.95],"radius":1.1})
)).extrude({ offset: [0, 0, 3] });
}


function l_case_border_extrude_16_outline_fn(){
    return new CSG.Path2D([[27,-148],[37,-148]]).appendPoint([37,-153.75]).appendArc([44,-160.75],{"radius":7,"clockwise":false,"large":false}).appendPoint([60,-160.75]).appendArc([67,-153.75],{"radius":7,"clockwise":false,"large":false}).appendPoint([67,-149.53]).appendPoint([77,-149.53]).appendArc([84,-142.53],{"radius":7,"clockwise":false,"large":false}).appendPoint([84,-136.78]).appendPoint([89.5965289,-136.78]).appendArc([94.5038705,-139.3123961],{"radius":7,"clockwise":false,"large":false}).appendPoint([92.6186982,-150.0037394]).appendArc([98.2968154,-158.1129309],{"radius":7,"clockwise":false,"large":false}).appendArc([98.2968153,-158.1129309],{"radius":4,"clockwise":false,"large":false}).appendPoint([113.7034028,-160.8295279]).appendPoint([127.8811056,-167.4406993]).appendArc([128.0794093,-167.52948],{"radius":7,"clockwise":false,"large":false}).appendArc([128.2651015,-167.6405509],{"radius":7,"clockwise":false,"large":false}).appendPoint([142.1215079,-175.6405509]).appendArc([151.6836857,-173.0783731],{"radius":7,"clockwise":false,"large":false}).appendPoint([159.6836857,-159.2219667]).appendArc([157.1215079,-149.6597889],{"radius":7,"clockwise":false,"large":false}).appendPoint([143.2651015,-141.6597889]).appendArc([141.866452,-141.0448171],{"radius":7,"clockwise":false,"large":false}).appendArc([140.560464,-140.2518437],{"radius":7,"clockwise":false,"large":false}).appendPoint([138.5835638,-139.33]).appendPoint([145,-139.33]).appendArc([152,-132.33],{"radius":7,"clockwise":false,"large":false}).appendPoint([152,-116.33]).appendArc([151.98212,-115.83],{"radius":7,"clockwise":false,"large":false}).appendArc([152,-115.33],{"radius":7,"clockwise":false,"large":false}).appendPoint([152,-99.33]).appendArc([151.98212,-98.83],{"radius":7,"clockwise":false,"large":false}).appendArc([152,-98.33],{"radius":7,"clockwise":false,"large":false}).appendPoint([152,-82.33]).appendArc([145,-75.33],{"radius":7,"clockwise":false,"large":false}).appendPoint([135,-75.33]).appendPoint([135,-68.73]).appendArc([128,-61.73],{"radius":7,"clockwise":false,"large":false}).appendPoint([122,-61.73]).appendPoint([122,-55.77]).appendArc([118.75,-49.8592048],{"radius":7,"clockwise":false,"large":false}).appendPoint([118.75,-40.77]).appendArc([111.75,-33.77],{"radius":7,"clockwise":false,"large":false}).appendPoint([67.75,-33.77]).appendArc([60.75,-40.77],{"radius":7,"clockwise":false,"large":false}).appendPoint([60.75,-51.5344657]).appendArc([54,-58.53],{"radius":7,"clockwise":false,"large":false}).appendPoint([54,-62.75]).appendPoint([44,-62.75]).appendArc([37.5628034,-67],{"radius":7,"clockwise":false,"large":false}).appendPoint([27,-67]).appendArc([20,-74],{"radius":7,"clockwise":false,"large":false}).appendPoint([20,-90]).appendArc([20.01788,-90.5],{"radius":7,"clockwise":false,"large":false}).appendArc([20,-91],{"radius":7,"clockwise":false,"large":false}).appendPoint([20,-107]).appendArc([20.01788,-107.5],{"radius":7,"clockwise":false,"large":false}).appendArc([20,-108],{"radius":7,"clockwise":false,"large":false}).appendPoint([20,-124]).appendArc([20.01788,-124.5],{"radius":7,"clockwise":false,"large":false}).appendArc([20,-125],{"radius":7,"clockwise":false,"large":false}).appendPoint([20,-141]).appendArc([27,-148],{"radius":7,"clockwise":false,"large":false}).close().innerToCAG()
.subtract(
    new CSG.Path2D([[27,-146],[39,-146]]).appendPoint([39,-153.75]).appendArc([44,-158.75],{"radius":5,"clockwise":false,"large":false}).appendPoint([60,-158.75]).appendArc([65,-153.75],{"radius":5,"clockwise":false,"large":false}).appendPoint([65,-147.53]).appendPoint([77,-147.53]).appendArc([82,-142.53],{"radius":5,"clockwise":false,"large":false}).appendPoint([82,-134.78]).appendPoint([90.6413878,-134.78]).appendArc([95,-137.33],{"radius":5,"clockwise":false,"large":false}).appendPoint([96.8842737,-137.33]).appendPoint([94.5883137,-150.3510358]).appendArc([98.6433075,-156.1431735],{"radius":5,"clockwise":false,"large":false}).appendPoint([114.3100036,-158.9056348]).appendPoint([128.7271527,-165.6284618]).appendArc([129.0065139,-165.7485283],{"radius":5,"clockwise":false,"large":false}).appendArc([129.2651015,-165.9085001],{"radius":5,"clockwise":false,"large":false}).appendPoint([143.1215079,-173.9085001]).appendArc([149.9516349,-172.0783731],{"radius":5,"clockwise":false,"large":false}).appendPoint([157.9516349,-158.2219667]).appendArc([156.1215079,-151.3918397],{"radius":5,"clockwise":false,"large":false}).appendPoint([142.2651015,-143.3918397]).appendArc([140.9226686,-142.8578081],{"radius":5,"clockwise":false,"large":false}).appendArc([139.7152275,-142.0644593],{"radius":5,"clockwise":false,"large":false}).appendPoint([132.1408068,-138.5324488]).appendArc([132.7370877,-137.33],{"radius":5,"clockwise":false,"large":false}).appendPoint([145,-137.33]).appendArc([150,-132.33],{"radius":5,"clockwise":false,"large":false}).appendPoint([150,-116.33]).appendArc([149.9749372,-115.83],{"radius":5,"clockwise":false,"large":false}).appendArc([150,-115.33],{"radius":5,"clockwise":false,"large":false}).appendPoint([150,-99.33]).appendArc([149.9749372,-98.83],{"radius":5,"clockwise":false,"large":false}).appendArc([150,-98.33],{"radius":5,"clockwise":false,"large":false}).appendPoint([150,-82.33]).appendArc([145,-77.33],{"radius":5,"clockwise":false,"large":false}).appendPoint([133,-77.33]).appendPoint([133,-68.73]).appendArc([128,-63.73],{"radius":5,"clockwise":false,"large":false}).appendPoint([120,-63.73]).appendPoint([120,-55.77]).appendArc([116.75,-51.0862515],{"radius":5,"clockwise":false,"large":false}).appendPoint([116.75,-40.77]).appendArc([111.75,-35.77],{"radius":5,"clockwise":false,"large":false}).appendPoint([67.75,-35.77]).appendArc([62.75,-40.77],{"radius":5,"clockwise":false,"large":false}).appendPoint([62.75,-53.53]).appendPoint([61,-53.53]).appendArc([56,-58.53],{"radius":5,"clockwise":false,"large":false}).appendPoint([56,-64.75]).appendPoint([44,-64.75]).appendArc([39.05657,-69],{"radius":5,"clockwise":false,"large":false}).appendPoint([27,-69]).appendArc([22,-74],{"radius":5,"clockwise":false,"large":false}).appendPoint([22,-90]).appendArc([22.0250628,-90.5],{"radius":5,"clockwise":false,"large":false}).appendArc([22,-91],{"radius":5,"clockwise":false,"large":false}).appendPoint([22,-107]).appendArc([22.0250628,-107.5],{"radius":5,"clockwise":false,"large":false}).appendArc([22,-108],{"radius":5,"clockwise":false,"large":false}).appendPoint([22,-124]).appendArc([22.0250628,-124.5],{"radius":5,"clockwise":false,"large":false}).appendArc([22,-125],{"radius":5,"clockwise":false,"large":false}).appendPoint([22,-141]).appendArc([27,-146],{"radius":5,"clockwise":false,"large":false}).close().innerToCAG()
).extrude({ offset: [0, 0, 16] });
}


function l_usbc_border_outline_extrude_10_outline_fn(){
    return new CSG.Path2D([[74.25,-55.27],[89.25,-55.27]]).appendPoint([89.25,-40.27]).appendPoint([74.25,-40.27]).appendPoint([74.25,-55.27]).close().innerToCAG()
.extrude({ offset: [0, 0, 10] });
}


function l_coverpart_switch_plate_outline_extrude_3_outline_fn(){
    return new CSG.Path2D([[27,-144],[41,-144]]).appendPoint([41,-153.75]).appendArc([44,-156.75],{"radius":3,"clockwise":false,"large":false}).appendPoint([60,-156.75]).appendArc([63,-153.75],{"radius":3,"clockwise":false,"large":false}).appendPoint([63,-145.53]).appendPoint([77,-145.53]).appendArc([80,-142.53],{"radius":3,"clockwise":false,"large":false}).appendPoint([80,-132.78]).appendPoint([92.033942,-132.78]).appendArc([95,-135.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([99.2677808,-135.33]).appendPoint([96.5579293,-150.6983321]).appendArc([98.9914081,-154.1736999],{"radius":3,"clockwise":false,"large":false}).appendPoint([114.7483321,-156.9520707]).appendArc([114.9180932,-156.9770215],{"radius":3,"clockwise":false,"large":false}).appendArc([115.0714646,-157.053954],{"radius":3,"clockwise":false,"large":false}).appendPoint([129.5723892,-163.8158462]).appendArc([129.9385037,-163.9581925],{"radius":3,"clockwise":false,"large":false}).appendArc([130.2651015,-164.1764493],{"radius":3,"clockwise":false,"large":false}).appendPoint([144.1215079,-172.1764493]).appendArc([148.2195841,-171.0783731],{"radius":3,"clockwise":false,"large":false}).appendPoint([156.2195841,-157.2219667]).appendArc([155.1215079,-153.1238905],{"radius":3,"clockwise":false,"large":false}).appendPoint([141.2651015,-145.1238905]).appendArc([139.9493024,-144.727627],{"radius":3,"clockwise":false,"large":false}).appendArc([138.869991,-143.8770748],{"radius":3,"clockwise":false,"large":false}).appendPoint([127.8320535,-138.73]).appendPoint([128,-138.73]).appendArc([131,-135.73],{"radius":3,"clockwise":false,"large":false}).appendPoint([131,-135.33]).appendPoint([145,-135.33]).appendArc([148,-132.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([148,-116.33]).appendArc([147.9580399,-115.83],{"radius":3,"clockwise":false,"large":false}).appendArc([148,-115.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([148,-99.33]).appendArc([147.9580399,-98.83],{"radius":3,"clockwise":false,"large":false}).appendArc([148,-98.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([148,-82.33]).appendArc([145,-79.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([131,-79.33]).appendPoint([131,-68.73]).appendArc([128,-65.73],{"radius":3,"clockwise":false,"large":false}).appendPoint([114,-65.73]).appendPoint([114,-65.33]).appendArc([111,-62.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([96.966058,-62.33]).appendArc([94,-59.78],{"radius":3,"clockwise":false,"large":false}).appendPoint([80,-59.78]).appendPoint([80,-58.53]).appendArc([77,-55.53],{"radius":3,"clockwise":false,"large":false}).appendPoint([61,-55.53]).appendArc([58,-58.53],{"radius":3,"clockwise":false,"large":false}).appendPoint([58,-66.75]).appendPoint([44,-66.75]).appendArc([41,-69.75],{"radius":3,"clockwise":false,"large":false}).appendPoint([41,-71]).appendPoint([27,-71]).appendArc([24,-74],{"radius":3,"clockwise":false,"large":false}).appendPoint([24,-90]).appendArc([24.0419601,-90.5],{"radius":3,"clockwise":false,"large":false}).appendArc([24,-91],{"radius":3,"clockwise":false,"large":false}).appendPoint([24,-107]).appendArc([24.0419601,-107.5],{"radius":3,"clockwise":false,"large":false}).appendArc([24,-108],{"radius":3,"clockwise":false,"large":false}).appendPoint([24,-124]).appendArc([24.0419601,-124.5],{"radius":3,"clockwise":false,"large":false}).appendArc([24,-125],{"radius":3,"clockwise":false,"large":false}).appendPoint([24,-141]).appendArc([27,-144],{"radius":3,"clockwise":false,"large":false}).close().innerToCAG()
.subtract(
    CAG.circle({"center":[119.0636178,-153.3434671],"radius":1.1})
.union(
    CAG.circle({"center":[114.05,-133.68],"radius":1.1})
).union(
    CAG.circle({"center":[114.05,-82.68],"radius":1.1})
).union(
    CAG.circle({"center":[29.05,-138.95],"radius":1.1})
).union(
    CAG.circle({"center":[29.05,-87.95],"radius":1.1})
).union(
    new CSG.Path2D([[137.9805171,-159.9129575],[143.9560923,-163.3629575]]).appendPoint([147.4060923,-157.3873823]).appendPoint([141.4305171,-153.9373823]).appendPoint([137.9805171,-159.9129575]).close().innerToCAG()
).union(
    new CSG.Path2D([[65.55,-69.98],[72.45,-69.98]]).appendPoint([72.45,-63.08]).appendPoint([65.55,-63.08]).appendPoint([65.55,-69.98]).close().innerToCAG()
).union(
    new CSG.Path2D([[48.55,-81.2],[55.45,-81.2]]).appendPoint([55.45,-74.3]).appendPoint([48.55,-74.3]).appendPoint([48.55,-81.2]).close().innerToCAG()
).union(
    new CSG.Path2D([[48.55,-98.2],[55.45,-98.2]]).appendPoint([55.45,-91.3]).appendPoint([48.55,-91.3]).appendPoint([48.55,-98.2]).close().innerToCAG()
).union(
    new CSG.Path2D([[48.55,-115.2],[55.45,-115.2]]).appendPoint([55.45,-108.3]).appendPoint([48.55,-108.3]).appendPoint([48.55,-115.2]).close().innerToCAG()
).union(
    new CSG.Path2D([[48.55,-132.2],[55.45,-132.2]]).appendPoint([55.45,-125.3]).appendPoint([48.55,-125.3]).appendPoint([48.55,-132.2]).close().innerToCAG()
).union(
    new CSG.Path2D([[48.55,-149.2],[55.45,-149.2]]).appendPoint([55.45,-142.3]).appendPoint([48.55,-142.3]).appendPoint([48.55,-149.2]).close().innerToCAG()
).union(
    new CSG.Path2D([[31.55,-85.45],[38.45,-85.45]]).appendPoint([38.45,-78.55]).appendPoint([31.55,-78.55]).appendPoint([31.55,-85.45]).close().innerToCAG()
).union(
    new CSG.Path2D([[31.55,-102.45],[38.45,-102.45]]).appendPoint([38.45,-95.55]).appendPoint([31.55,-95.55]).appendPoint([31.55,-102.45]).close().innerToCAG()
).union(
    new CSG.Path2D([[31.55,-119.45],[38.45,-119.45]]).appendPoint([38.45,-112.55]).appendPoint([31.55,-112.55]).appendPoint([31.55,-119.45]).close().innerToCAG()
).union(
    new CSG.Path2D([[31.55,-136.45],[38.45,-136.45]]).appendPoint([38.45,-129.55]).appendPoint([31.55,-129.55]).appendPoint([31.55,-136.45]).close().innerToCAG()
).union(
    new CSG.Path2D([[133.55,-93.78],[140.45,-93.78]]).appendPoint([140.45,-86.88]).appendPoint([133.55,-86.88]).appendPoint([133.55,-93.78]).close().innerToCAG()
).union(
    new CSG.Path2D([[133.55,-110.78],[140.45,-110.78]]).appendPoint([140.45,-103.88]).appendPoint([133.55,-103.88]).appendPoint([133.55,-110.78]).close().innerToCAG()
).union(
    new CSG.Path2D([[133.55,-127.78],[140.45,-127.78]]).appendPoint([140.45,-120.88]).appendPoint([133.55,-120.88]).appendPoint([133.55,-127.78]).close().innerToCAG()
).union(
    new CSG.Path2D([[116.55,-80.18],[123.45,-80.18]]).appendPoint([123.45,-73.28]).appendPoint([116.55,-73.28]).appendPoint([116.55,-80.18]).close().innerToCAG()
).union(
    new CSG.Path2D([[116.55,-97.18],[123.45,-97.18]]).appendPoint([123.45,-90.28]).appendPoint([116.55,-90.28]).appendPoint([116.55,-97.18]).close().innerToCAG()
).union(
    new CSG.Path2D([[116.55,-114.18],[123.45,-114.18]]).appendPoint([123.45,-107.28]).appendPoint([116.55,-107.28]).appendPoint([116.55,-114.18]).close().innerToCAG()
).union(
    new CSG.Path2D([[116.55,-131.18],[123.45,-131.18]]).appendPoint([123.45,-124.28]).appendPoint([116.55,-124.28]).appendPoint([116.55,-131.18]).close().innerToCAG()
).union(
    new CSG.Path2D([[99.55,-76.78],[106.45,-76.78]]).appendPoint([106.45,-69.88]).appendPoint([99.55,-69.88]).appendPoint([99.55,-76.78]).close().innerToCAG()
).union(
    new CSG.Path2D([[99.55,-93.78],[106.45,-93.78]]).appendPoint([106.45,-86.88]).appendPoint([99.55,-86.88]).appendPoint([99.55,-93.78]).close().innerToCAG()
).union(
    new CSG.Path2D([[99.55,-110.78],[106.45,-110.78]]).appendPoint([106.45,-103.88]).appendPoint([99.55,-103.88]).appendPoint([99.55,-110.78]).close().innerToCAG()
).union(
    new CSG.Path2D([[99.55,-127.78],[106.45,-127.78]]).appendPoint([106.45,-120.88]).appendPoint([99.55,-120.88]).appendPoint([99.55,-127.78]).close().innerToCAG()
).union(
    new CSG.Path2D([[82.55,-74.23],[89.45,-74.23]]).appendPoint([89.45,-67.33]).appendPoint([82.55,-67.33]).appendPoint([82.55,-74.23]).close().innerToCAG()
).union(
    new CSG.Path2D([[82.55,-91.23],[89.45,-91.23]]).appendPoint([89.45,-84.33]).appendPoint([82.55,-84.33]).appendPoint([82.55,-91.23]).close().innerToCAG()
).union(
    new CSG.Path2D([[82.55,-108.23],[89.45,-108.23]]).appendPoint([89.45,-101.33]).appendPoint([82.55,-101.33]).appendPoint([82.55,-108.23]).close().innerToCAG()
).union(
    new CSG.Path2D([[82.55,-125.23],[89.45,-125.23]]).appendPoint([89.45,-118.33]).appendPoint([82.55,-118.33]).appendPoint([82.55,-125.23]).close().innerToCAG()
).union(
    new CSG.Path2D([[65.55,-86.98],[72.45,-86.98]]).appendPoint([72.45,-80.08]).appendPoint([65.55,-80.08]).appendPoint([65.55,-86.98]).close().innerToCAG()
).union(
    new CSG.Path2D([[65.55,-103.98],[72.45,-103.98]]).appendPoint([72.45,-97.08]).appendPoint([65.55,-97.08]).appendPoint([65.55,-103.98]).close().innerToCAG()
).union(
    new CSG.Path2D([[65.55,-120.98],[72.45,-120.98]]).appendPoint([72.45,-114.08]).appendPoint([65.55,-114.08]).appendPoint([65.55,-120.98]).close().innerToCAG()
).union(
    new CSG.Path2D([[65.55,-137.98],[72.45,-137.98]]).appendPoint([72.45,-131.08]).appendPoint([65.55,-131.08]).appendPoint([65.55,-137.98]).close().innerToCAG()
).union(
    new CSG.Path2D([[104.783327,-147.5285005],[111.5785005,-148.726673]]).appendPoint([112.776673,-141.9314995]).appendPoint([105.9814995,-140.733327]).appendPoint([104.783327,-147.5285005]).close().innerToCAG()
).union(
    new CSG.Path2D([[122.3859329,-152.1342433],[128.6394567,-155.0503093]]).appendPoint([131.5555227,-148.7967855]).appendPoint([125.3019989,-145.8807195]).appendPoint([122.3859329,-152.1342433]).close().innerToCAG()
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
                let l_3d_preview__part_1 = l_case_border_extrude_16_outline_fn();

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
                let l_3d_preview__part_2 = l_usbc_border_outline_extrude_10_outline_fn();

                // make sure that rotations are relative
                let l_3d_preview__part_2_bounds = l_3d_preview__part_2.getBounds();
                let l_3d_preview__part_2_x = l_3d_preview__part_2_bounds[0].x + (l_3d_preview__part_2_bounds[1].x - l_3d_preview__part_2_bounds[0].x) / 2
                let l_3d_preview__part_2_y = l_3d_preview__part_2_bounds[0].y + (l_3d_preview__part_2_bounds[1].y - l_3d_preview__part_2_bounds[0].y) / 2
                l_3d_preview__part_2 = translate([-l_3d_preview__part_2_x, -l_3d_preview__part_2_y, 0], l_3d_preview__part_2);
                l_3d_preview__part_2 = rotate([0,0,0], l_3d_preview__part_2);
                l_3d_preview__part_2 = translate([l_3d_preview__part_2_x, l_3d_preview__part_2_y, 0], l_3d_preview__part_2);

                l_3d_preview__part_2 = translate([-20,5,3], l_3d_preview__part_2);
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

        