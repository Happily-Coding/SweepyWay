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




                function l_case_3d_case_fn() {
                    

                // creating part 0 of case l_case_3d
                let l_case_3d__part_0 = l_case_bottom_extrude_3_outline_fn();

                // make sure that rotations are relative
                let l_case_3d__part_0_bounds = l_case_3d__part_0.getBounds();
                let l_case_3d__part_0_x = l_case_3d__part_0_bounds[0].x + (l_case_3d__part_0_bounds[1].x - l_case_3d__part_0_bounds[0].x) / 2
                let l_case_3d__part_0_y = l_case_3d__part_0_bounds[0].y + (l_case_3d__part_0_bounds[1].y - l_case_3d__part_0_bounds[0].y) / 2
                l_case_3d__part_0 = translate([-l_case_3d__part_0_x, -l_case_3d__part_0_y, 0], l_case_3d__part_0);
                l_case_3d__part_0 = rotate([0,0,0], l_case_3d__part_0);
                l_case_3d__part_0 = translate([l_case_3d__part_0_x, l_case_3d__part_0_y, 0], l_case_3d__part_0);

                l_case_3d__part_0 = translate([0,0,0], l_case_3d__part_0);
                let result = l_case_3d__part_0;
                
            

                // creating part 1 of case l_case_3d
                let l_case_3d__part_1 = l_case_border_extrude_16_outline_fn();

                // make sure that rotations are relative
                let l_case_3d__part_1_bounds = l_case_3d__part_1.getBounds();
                let l_case_3d__part_1_x = l_case_3d__part_1_bounds[0].x + (l_case_3d__part_1_bounds[1].x - l_case_3d__part_1_bounds[0].x) / 2
                let l_case_3d__part_1_y = l_case_3d__part_1_bounds[0].y + (l_case_3d__part_1_bounds[1].y - l_case_3d__part_1_bounds[0].y) / 2
                l_case_3d__part_1 = translate([-l_case_3d__part_1_x, -l_case_3d__part_1_y, 0], l_case_3d__part_1);
                l_case_3d__part_1 = rotate([0,0,0], l_case_3d__part_1);
                l_case_3d__part_1 = translate([l_case_3d__part_1_x, l_case_3d__part_1_y, 0], l_case_3d__part_1);

                l_case_3d__part_1 = translate([0,0,0], l_case_3d__part_1);
                result = result.union(l_case_3d__part_1);
                
            

                // creating part 2 of case l_case_3d
                let l_case_3d__part_2 = l_usbc_border_outline_extrude_10_outline_fn();

                // make sure that rotations are relative
                let l_case_3d__part_2_bounds = l_case_3d__part_2.getBounds();
                let l_case_3d__part_2_x = l_case_3d__part_2_bounds[0].x + (l_case_3d__part_2_bounds[1].x - l_case_3d__part_2_bounds[0].x) / 2
                let l_case_3d__part_2_y = l_case_3d__part_2_bounds[0].y + (l_case_3d__part_2_bounds[1].y - l_case_3d__part_2_bounds[0].y) / 2
                l_case_3d__part_2 = translate([-l_case_3d__part_2_x, -l_case_3d__part_2_y, 0], l_case_3d__part_2);
                l_case_3d__part_2 = rotate([0,0,0], l_case_3d__part_2);
                l_case_3d__part_2 = translate([l_case_3d__part_2_x, l_case_3d__part_2_y, 0], l_case_3d__part_2);

                l_case_3d__part_2 = translate([-20,5,3], l_case_3d__part_2);
                result = result.subtract(l_case_3d__part_2);
                
            
                    return result;
                }
            
            
        
            function main() {
                return l_case_3d_case_fn();
            }

        