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


function r_standoff_bosses_extrude_3_outline_fn(){
    return CAG.circle({"center":[208.2895731,-160.2956003],"radius":2.1})
.subtract(
    CAG.circle({"center":[208.2895731,-160.2956003],"radius":1.1})
).union(
    CAG.circle({"center":[211.2,-132.63],"radius":2.1})
.subtract(
    CAG.circle({"center":[211.2,-132.63],"radius":1.1})
)).union(
    CAG.circle({"center":[211.2,-80.13],"radius":2.1})
.subtract(
    CAG.circle({"center":[211.2,-80.13],"radius":1.1})
)).union(
    CAG.circle({"center":[296.2,-137.15],"radius":2.1})
.subtract(
    CAG.circle({"center":[296.2,-137.15],"radius":1.1})
)).union(
    CAG.circle({"center":[296.2,-86.15],"radius":2.1})
.subtract(
    CAG.circle({"center":[296.2,-86.15],"radius":1.1})
)).extrude({ offset: [0, 0, 3] });
}


function r_case_border_extrude_11_2_outline_fn(){
    return new CSG.Path2D([[303,-148],[313,-148]]).appendArc([320,-141],{"radius":7,"clockwise":false,"large":false}).appendPoint([320,-125]).appendArc([319.98212,-124.5],{"radius":7,"clockwise":false,"large":false}).appendArc([320,-124],{"radius":7,"clockwise":false,"large":false}).appendPoint([320,-108]).appendArc([319.98212,-107.5],{"radius":7,"clockwise":false,"large":false}).appendArc([320,-107],{"radius":7,"clockwise":false,"large":false}).appendPoint([320,-91]).appendArc([319.98212,-90.5],{"radius":7,"clockwise":false,"large":false}).appendArc([320,-90],{"radius":7,"clockwise":false,"large":false}).appendPoint([320,-74]).appendArc([313,-67],{"radius":7,"clockwise":false,"large":false}).appendPoint([302.4371966,-67]).appendArc([296,-62.75],{"radius":7,"clockwise":false,"large":false}).appendPoint([286,-62.75]).appendPoint([286,-58.53]).appendArc([279.25,-51.5344657],{"radius":7,"clockwise":false,"large":false}).appendPoint([279.25,-40.77]).appendArc([272.25,-33.77],{"radius":7,"clockwise":false,"large":false}).appendPoint([228.25,-33.77]).appendArc([221.25,-40.77],{"radius":7,"clockwise":false,"large":false}).appendPoint([221.25,-49.8592048]).appendArc([218,-55.77],{"radius":7,"clockwise":false,"large":false}).appendPoint([218,-61.73]).appendPoint([212,-61.73]).appendArc([205,-68.73],{"radius":7,"clockwise":false,"large":false}).appendPoint([205,-75.33]).appendPoint([195,-75.33]).appendArc([188,-82.33],{"radius":7,"clockwise":false,"large":false}).appendPoint([188,-98.33]).appendArc([188.01788,-98.83],{"radius":7,"clockwise":false,"large":false}).appendArc([188,-99.33],{"radius":7,"clockwise":false,"large":false}).appendPoint([188,-115.33]).appendArc([188.01788,-115.83],{"radius":7,"clockwise":false,"large":false}).appendArc([188,-116.33],{"radius":7,"clockwise":false,"large":false}).appendPoint([188,-132.33]).appendArc([195,-139.33],{"radius":7,"clockwise":false,"large":false}).appendPoint([201.4164361,-139.33]).appendPoint([199.4395359,-140.2518437]).appendArc([198.1335481,-141.0448171],{"radius":7,"clockwise":false,"large":false}).appendArc([196.7348985,-141.6597889],{"radius":7,"clockwise":false,"large":false}).appendPoint([182.8784921,-149.6597889]).appendArc([180.3163143,-159.2219667],{"radius":7,"clockwise":false,"large":false}).appendPoint([188.3163143,-173.0783731]).appendArc([197.8784921,-175.6405509],{"radius":7,"clockwise":false,"large":false}).appendPoint([211.7348985,-167.6405509]).appendArc([211.9205907,-167.52948],{"radius":7,"clockwise":false,"large":false}).appendArc([212.1180838,-167.4410773],{"radius":7,"clockwise":false,"large":false}).appendPoint([226.2965972,-160.8295279]).appendPoint([241.7031847,-158.1129309]).appendArc([241.7045303,-158.1126934],{"radius":4,"clockwise":false,"large":false}).appendArc([247.3813017,-150.0037394],{"radius":7,"clockwise":false,"large":false}).appendPoint([245.4961294,-139.3123961]).appendArc([250.4034711,-136.78],{"radius":7,"clockwise":false,"large":false}).appendPoint([256,-136.78]).appendPoint([256,-142.53]).appendArc([263,-149.53],{"radius":7,"clockwise":false,"large":false}).appendPoint([273,-149.53]).appendPoint([273,-153.75]).appendArc([280,-160.75],{"radius":7,"clockwise":false,"large":false}).appendPoint([296,-160.75]).appendArc([303,-153.75],{"radius":7,"clockwise":false,"large":false}).appendPoint([303,-148]).close().innerToCAG()
.subtract(
    new CSG.Path2D([[301,-146],[313,-146]]).appendArc([318,-141],{"radius":5,"clockwise":false,"large":false}).appendPoint([318,-125]).appendArc([317.9749372,-124.5],{"radius":5,"clockwise":false,"large":false}).appendArc([318,-124],{"radius":5,"clockwise":false,"large":false}).appendPoint([318,-108]).appendArc([317.9749372,-107.5],{"radius":5,"clockwise":false,"large":false}).appendArc([318,-107],{"radius":5,"clockwise":false,"large":false}).appendPoint([318,-91]).appendArc([317.9749372,-90.5],{"radius":5,"clockwise":false,"large":false}).appendArc([318,-90],{"radius":5,"clockwise":false,"large":false}).appendPoint([318,-74]).appendArc([313,-69],{"radius":5,"clockwise":false,"large":false}).appendPoint([300.94343,-69]).appendArc([296,-64.75],{"radius":5,"clockwise":false,"large":false}).appendPoint([284,-64.75]).appendPoint([284,-58.53]).appendArc([279,-53.53],{"radius":5,"clockwise":false,"large":false}).appendPoint([277.25,-53.53]).appendPoint([277.25,-40.77]).appendArc([272.25,-35.77],{"radius":5,"clockwise":false,"large":false}).appendPoint([228.25,-35.77]).appendArc([223.25,-40.77],{"radius":5,"clockwise":false,"large":false}).appendPoint([223.25,-51.0862515]).appendArc([220,-55.77],{"radius":5,"clockwise":false,"large":false}).appendPoint([220,-63.73]).appendPoint([212,-63.73]).appendArc([207,-68.73],{"radius":5,"clockwise":false,"large":false}).appendPoint([207,-77.33]).appendPoint([195,-77.33]).appendArc([190,-82.33],{"radius":5,"clockwise":false,"large":false}).appendPoint([190,-98.33]).appendArc([190.0250628,-98.83],{"radius":5,"clockwise":false,"large":false}).appendArc([190,-99.33],{"radius":5,"clockwise":false,"large":false}).appendPoint([190,-115.33]).appendArc([190.0250628,-115.83],{"radius":5,"clockwise":false,"large":false}).appendArc([190,-116.33],{"radius":5,"clockwise":false,"large":false}).appendPoint([190,-132.33]).appendArc([195,-137.33],{"radius":5,"clockwise":false,"large":false}).appendPoint([207.2629123,-137.33]).appendArc([207.8591932,-138.5324488],{"radius":5,"clockwise":false,"large":false}).appendPoint([200.2847725,-142.0644592]).appendArc([199.0773315,-142.8578081],{"radius":5,"clockwise":false,"large":false}).appendArc([197.7348985,-143.3918397],{"radius":5,"clockwise":false,"large":false}).appendPoint([183.8784921,-151.3918397]).appendArc([182.0483651,-158.2219667],{"radius":5,"clockwise":false,"large":false}).appendPoint([190.0483651,-172.0783731]).appendArc([196.8784921,-173.9085001],{"radius":5,"clockwise":false,"large":false}).appendPoint([210.7348985,-165.9085001]).appendArc([210.993486,-165.7485284],{"radius":5,"clockwise":false,"large":false}).appendArc([211.2728473,-165.6284617],{"radius":5,"clockwise":false,"large":false}).appendPoint([225.6899964,-158.9056348]).appendPoint([241.3558883,-156.1433154]).appendArc([245.4116862,-150.3510357],{"radius":5,"clockwise":false,"large":false}).appendPoint([243.1157264,-137.33]).appendPoint([245,-137.33]).appendArc([249.3586122,-134.78],{"radius":5,"clockwise":false,"large":false}).appendPoint([258,-134.78]).appendPoint([258,-142.53]).appendArc([263,-147.53],{"radius":5,"clockwise":false,"large":false}).appendPoint([275,-147.53]).appendPoint([275,-153.75]).appendArc([280,-158.75],{"radius":5,"clockwise":false,"large":false}).appendPoint([296,-158.75]).appendArc([301,-153.75],{"radius":5,"clockwise":false,"large":false}).appendPoint([301,-146]).close().innerToCAG()
).extrude({ offset: [0, 0, 11.2] });
}


function r_usbc_border_outline_extrude_7_199999999999999_outline_fn(){
    return new CSG.Path2D([[250.75,-55.27],[265.75,-55.27]]).appendPoint([265.75,-40.27]).appendPoint([250.75,-40.27]).appendPoint([250.75,-55.27]).close().innerToCAG()
.extrude({ offset: [0, 0, 7.199999999999999] });
}


function r_hood_footprint_extrude_17_08_outline_fn(){
    return new CSG.Path2D([[275.25,-55.53],[275.25,-40.77]]).appendArc([272.25,-37.77],{"radius":3,"clockwise":false,"large":false}).appendPoint([228.25,-37.77]).appendArc([225.25,-40.77],{"radius":3,"clockwise":false,"large":false}).appendPoint([225.25,-64.77]).appendArc([225.4077474,-65.73],{"radius":3,"clockwise":false,"large":false}).appendPoint([226,-65.73]).appendPoint([226,-65.33]).appendArc([229,-62.33],{"radius":3,"clockwise":true,"large":false}).appendPoint([243.033942,-62.33]).appendArc([246,-59.78],{"radius":3,"clockwise":true,"large":false}).appendPoint([260,-59.78]).appendPoint([260,-58.53]).appendArc([263,-55.53],{"radius":3,"clockwise":true,"large":false}).appendPoint([275.25,-55.53]).close().innerToCAG()
.extrude({ offset: [0, 0, 17.08] });
}


function r_hood_cavity_extrude_17_08_outline_fn(){
    return new CSG.Path2D([[274.05,-54.33],[274.05,-40.77]]).appendArc([272.25,-38.97],{"radius":1.8,"clockwise":false,"large":false}).appendPoint([228.25,-38.97]).appendArc([226.45,-40.77],{"radius":1.8,"clockwise":false,"large":false}).appendPoint([226.45,-61.9927107]).appendArc([229,-61.13],{"radius":4.2,"clockwise":true,"large":false}).appendPoint([242.137682,-61.13]).appendArc([246,-58.58],{"radius":4.2,"clockwise":true,"large":false}).appendPoint([258.8,-58.58]).appendPoint([258.8,-58.53]).appendArc([263,-54.33],{"radius":4.2,"clockwise":true,"large":false}).appendPoint([274.05,-54.33]).close().innerToCAG()
.extrude({ offset: [0, 0, 17.08] });
}


function r_hood_footprint_extrude_1_outline_fn(){
    return new CSG.Path2D([[275.25,-55.53],[275.25,-40.77]]).appendArc([272.25,-37.77],{"radius":3,"clockwise":false,"large":false}).appendPoint([228.25,-37.77]).appendArc([225.25,-40.77],{"radius":3,"clockwise":false,"large":false}).appendPoint([225.25,-64.77]).appendArc([225.4077474,-65.73],{"radius":3,"clockwise":false,"large":false}).appendPoint([226,-65.73]).appendPoint([226,-65.33]).appendArc([229,-62.33],{"radius":3,"clockwise":true,"large":false}).appendPoint([243.033942,-62.33]).appendArc([246,-59.78],{"radius":3,"clockwise":true,"large":false}).appendPoint([260,-59.78]).appendPoint([260,-58.53]).appendArc([263,-55.53],{"radius":3,"clockwise":true,"large":false}).appendPoint([275.25,-55.53]).close().innerToCAG()
.extrude({ offset: [0, 0, 1] });
}




                function r_case_3d_case_fn() {
                    

                // creating part 0 of case r_case_3d
                let r_case_3d__part_0 = r_case_bottom_extrude_3_outline_fn();

                // make sure that rotations are relative
                let r_case_3d__part_0_bounds = r_case_3d__part_0.getBounds();
                let r_case_3d__part_0_x = r_case_3d__part_0_bounds[0].x + (r_case_3d__part_0_bounds[1].x - r_case_3d__part_0_bounds[0].x) / 2
                let r_case_3d__part_0_y = r_case_3d__part_0_bounds[0].y + (r_case_3d__part_0_bounds[1].y - r_case_3d__part_0_bounds[0].y) / 2
                r_case_3d__part_0 = translate([-r_case_3d__part_0_x, -r_case_3d__part_0_y, 0], r_case_3d__part_0);
                r_case_3d__part_0 = rotate([0,0,0], r_case_3d__part_0);
                r_case_3d__part_0 = translate([r_case_3d__part_0_x, r_case_3d__part_0_y, 0], r_case_3d__part_0);

                r_case_3d__part_0 = translate([0,0,0], r_case_3d__part_0);
                let result = r_case_3d__part_0;
                
            

                // creating part 1 of case r_case_3d
                let r_case_3d__part_1 = r_standoff_bosses_extrude_3_outline_fn();

                // make sure that rotations are relative
                let r_case_3d__part_1_bounds = r_case_3d__part_1.getBounds();
                let r_case_3d__part_1_x = r_case_3d__part_1_bounds[0].x + (r_case_3d__part_1_bounds[1].x - r_case_3d__part_1_bounds[0].x) / 2
                let r_case_3d__part_1_y = r_case_3d__part_1_bounds[0].y + (r_case_3d__part_1_bounds[1].y - r_case_3d__part_1_bounds[0].y) / 2
                r_case_3d__part_1 = translate([-r_case_3d__part_1_x, -r_case_3d__part_1_y, 0], r_case_3d__part_1);
                r_case_3d__part_1 = rotate([0,0,0], r_case_3d__part_1);
                r_case_3d__part_1 = translate([r_case_3d__part_1_x, r_case_3d__part_1_y, 0], r_case_3d__part_1);

                r_case_3d__part_1 = translate([0,0,3], r_case_3d__part_1);
                result = result.union(r_case_3d__part_1);
                
            

                // creating part 2 of case r_case_3d
                let r_case_3d__part_2 = r_case_border_extrude_11_2_outline_fn();

                // make sure that rotations are relative
                let r_case_3d__part_2_bounds = r_case_3d__part_2.getBounds();
                let r_case_3d__part_2_x = r_case_3d__part_2_bounds[0].x + (r_case_3d__part_2_bounds[1].x - r_case_3d__part_2_bounds[0].x) / 2
                let r_case_3d__part_2_y = r_case_3d__part_2_bounds[0].y + (r_case_3d__part_2_bounds[1].y - r_case_3d__part_2_bounds[0].y) / 2
                r_case_3d__part_2 = translate([-r_case_3d__part_2_x, -r_case_3d__part_2_y, 0], r_case_3d__part_2);
                r_case_3d__part_2 = rotate([0,0,0], r_case_3d__part_2);
                r_case_3d__part_2 = translate([r_case_3d__part_2_x, r_case_3d__part_2_y, 0], r_case_3d__part_2);

                r_case_3d__part_2 = translate([0,0,0], r_case_3d__part_2);
                result = result.union(r_case_3d__part_2);
                
            

                // creating part 3 of case r_case_3d
                let r_case_3d__part_3 = r_usbc_border_outline_extrude_7_199999999999999_outline_fn();

                // make sure that rotations are relative
                let r_case_3d__part_3_bounds = r_case_3d__part_3.getBounds();
                let r_case_3d__part_3_x = r_case_3d__part_3_bounds[0].x + (r_case_3d__part_3_bounds[1].x - r_case_3d__part_3_bounds[0].x) / 2
                let r_case_3d__part_3_y = r_case_3d__part_3_bounds[0].y + (r_case_3d__part_3_bounds[1].y - r_case_3d__part_3_bounds[0].y) / 2
                r_case_3d__part_3 = translate([-r_case_3d__part_3_x, -r_case_3d__part_3_y, 0], r_case_3d__part_3);
                r_case_3d__part_3 = rotate([0,0,0], r_case_3d__part_3);
                r_case_3d__part_3 = translate([r_case_3d__part_3_x, r_case_3d__part_3_y, 0], r_case_3d__part_3);

                r_case_3d__part_3 = translate([0,7,3], r_case_3d__part_3);
                result = result.subtract(r_case_3d__part_3);
                
            

                // creating part 4 of case r_case_3d
                let r_case_3d__part_4 = r_hood_footprint_extrude_17_08_outline_fn();

                // make sure that rotations are relative
                let r_case_3d__part_4_bounds = r_case_3d__part_4.getBounds();
                let r_case_3d__part_4_x = r_case_3d__part_4_bounds[0].x + (r_case_3d__part_4_bounds[1].x - r_case_3d__part_4_bounds[0].x) / 2
                let r_case_3d__part_4_y = r_case_3d__part_4_bounds[0].y + (r_case_3d__part_4_bounds[1].y - r_case_3d__part_4_bounds[0].y) / 2
                r_case_3d__part_4 = translate([-r_case_3d__part_4_x, -r_case_3d__part_4_y, 0], r_case_3d__part_4);
                r_case_3d__part_4 = rotate([0,0,0], r_case_3d__part_4);
                r_case_3d__part_4 = translate([r_case_3d__part_4_x, r_case_3d__part_4_y, 0], r_case_3d__part_4);

                r_case_3d__part_4 = translate([0,0,2.6], r_case_3d__part_4);
                result = result.union(r_case_3d__part_4);
                
            

                // creating part 5 of case r_case_3d
                let r_case_3d__part_5 = r_hood_cavity_extrude_17_08_outline_fn();

                // make sure that rotations are relative
                let r_case_3d__part_5_bounds = r_case_3d__part_5.getBounds();
                let r_case_3d__part_5_x = r_case_3d__part_5_bounds[0].x + (r_case_3d__part_5_bounds[1].x - r_case_3d__part_5_bounds[0].x) / 2
                let r_case_3d__part_5_y = r_case_3d__part_5_bounds[0].y + (r_case_3d__part_5_bounds[1].y - r_case_3d__part_5_bounds[0].y) / 2
                r_case_3d__part_5 = translate([-r_case_3d__part_5_x, -r_case_3d__part_5_y, 0], r_case_3d__part_5);
                r_case_3d__part_5 = rotate([0,0,0], r_case_3d__part_5);
                r_case_3d__part_5 = translate([r_case_3d__part_5_x, r_case_3d__part_5_y, 0], r_case_3d__part_5);

                r_case_3d__part_5 = translate([0,0,2.6], r_case_3d__part_5);
                result = result.subtract(r_case_3d__part_5);
                
            

                // creating part 6 of case r_case_3d
                let r_case_3d__part_6 = r_hood_footprint_extrude_1_outline_fn();

                // make sure that rotations are relative
                let r_case_3d__part_6_bounds = r_case_3d__part_6.getBounds();
                let r_case_3d__part_6_x = r_case_3d__part_6_bounds[0].x + (r_case_3d__part_6_bounds[1].x - r_case_3d__part_6_bounds[0].x) / 2
                let r_case_3d__part_6_y = r_case_3d__part_6_bounds[0].y + (r_case_3d__part_6_bounds[1].y - r_case_3d__part_6_bounds[0].y) / 2
                r_case_3d__part_6 = translate([-r_case_3d__part_6_x, -r_case_3d__part_6_y, 0], r_case_3d__part_6);
                r_case_3d__part_6 = rotate([0,0,0], r_case_3d__part_6);
                r_case_3d__part_6 = translate([r_case_3d__part_6_x, r_case_3d__part_6_y, 0], r_case_3d__part_6);

                r_case_3d__part_6 = translate([0,0,19.08], r_case_3d__part_6);
                result = result.union(r_case_3d__part_6);
                
            
                    return result;
                }
            
            
        
            function main() {
                return r_case_3d_case_fn();
            }

        