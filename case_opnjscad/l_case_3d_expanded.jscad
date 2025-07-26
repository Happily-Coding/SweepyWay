function l_key_based_board_outline_with_extra_padding_extrude_3_outline_fn(){
    return new CSG.Path2D([[25.5,-145.5],[39.5,-145.5]]).appendPoint([39.5,-155.25]).appendArc([42.5,-158.25],{"radius":3,"clockwise":false,"large":false}).appendPoint([61.5,-158.25]).appendArc([64.5,-155.25],{"radius":3,"clockwise":false,"large":false}).appendPoint([64.5,-147.03]).appendPoint([78.5,-147.03]).appendArc([81.5,-144.03],{"radius":3,"clockwise":false,"large":false}).appendPoint([81.5,-134.28]).appendPoint([90.533942,-134.28]).appendArc([93.5,-136.83],{"radius":3,"clockwise":false,"large":false}).appendPoint([97.4801505,-136.83]).appendPoint([94.8202454,-151.9150714]).appendArc([97.2537242,-155.3904393],{"radius":3,"clockwise":false,"large":false}).appendPoint([114.4616542,-158.4246616]).appendPoint([129.233335,-165.3128094]).appendPoint([144.670546,-174.2254874]).appendArc([148.7686222,-173.1274112],{"radius":3,"clockwise":false,"large":false}).appendPoint([158.2686222,-156.6729286]).appendArc([157.170546,-152.5748524],{"radius":3,"clockwise":false,"large":false}).appendPoint([141.375523,-143.4555916]).appendArc([140.8633801,-143.1515405],{"radius":3,"clockwise":false,"large":false}).appendPoint([140.7880469,-143.1164121]).appendPoint([140.7160634,-143.0748524]).appendArc([140.1732471,-142.8297263],{"radius":3,"clockwise":false,"large":false}).appendPoint([131.9318672,-138.9867077]).appendArc([132.5,-137.23],{"radius":3,"clockwise":false,"large":false}).appendPoint([132.5,-136.83]).appendPoint([146.5,-136.83]).appendArc([149.5,-133.83],{"radius":3,"clockwise":false,"large":false}).appendPoint([149.5,-80.83]).appendArc([146.5,-77.83],{"radius":3,"clockwise":false,"large":false}).appendPoint([132.5,-77.83]).appendPoint([132.5,-67.23]).appendArc([129.5,-64.23],{"radius":3,"clockwise":false,"large":false}).appendPoint([115.5,-64.23]).appendPoint([115.5,-63.83]).appendArc([112.5,-60.83],{"radius":3,"clockwise":false,"large":false}).appendPoint([98.466058,-60.83]).appendArc([95.5,-58.28],{"radius":3,"clockwise":false,"large":false}).appendPoint([81.5,-58.28]).appendPoint([81.5,-57.03]).appendArc([78.5,-54.03],{"radius":3,"clockwise":false,"large":false}).appendPoint([59.5,-54.03]).appendArc([56.5,-57.03],{"radius":3,"clockwise":false,"large":false}).appendPoint([56.5,-65.25]).appendPoint([42.5,-65.25]).appendArc([39.5,-68.25],{"radius":3,"clockwise":false,"large":false}).appendPoint([39.5,-69.5]).appendPoint([25.5,-69.5]).appendArc([22.5,-72.5],{"radius":3,"clockwise":false,"large":false}).appendPoint([22.5,-142.5]).appendArc([25.5,-145.5],{"radius":3,"clockwise":false,"large":false}).close().innerToCAG()
.extrude({ offset: [0, 0, 3] });
}


function l_case_border_outline_extrude_16_outline_fn(){
    return new CSG.Path2D([[25.5,-145.5],[39.5,-145.5]]).appendPoint([39.5,-155.25]).appendArc([42.5,-158.25],{"radius":3,"clockwise":false,"large":false}).appendPoint([61.5,-158.25]).appendArc([64.5,-155.25],{"radius":3,"clockwise":false,"large":false}).appendPoint([64.5,-147.03]).appendPoint([78.5,-147.03]).appendArc([81.5,-144.03],{"radius":3,"clockwise":false,"large":false}).appendPoint([81.5,-134.28]).appendPoint([90.533942,-134.28]).appendArc([93.5,-136.83],{"radius":3,"clockwise":false,"large":false}).appendPoint([97.4801505,-136.83]).appendPoint([94.8202454,-151.9150714]).appendArc([97.2537242,-155.3904393],{"radius":3,"clockwise":false,"large":false}).appendPoint([114.4616542,-158.4246616]).appendPoint([129.233335,-165.3128094]).appendPoint([144.670546,-174.2254874]).appendArc([148.7686222,-173.1274112],{"radius":3,"clockwise":false,"large":false}).appendPoint([158.2686222,-156.6729286]).appendArc([157.170546,-152.5748524],{"radius":3,"clockwise":false,"large":false}).appendPoint([141.375523,-143.4555916]).appendArc([140.8633801,-143.1515405],{"radius":3,"clockwise":false,"large":false}).appendPoint([140.7880469,-143.1164121]).appendPoint([140.7160634,-143.0748524]).appendArc([140.1732471,-142.8297263],{"radius":3,"clockwise":false,"large":false}).appendPoint([131.9318672,-138.9867077]).appendArc([132.5,-137.23],{"radius":3,"clockwise":false,"large":false}).appendPoint([132.5,-136.83]).appendPoint([146.5,-136.83]).appendArc([149.5,-133.83],{"radius":3,"clockwise":false,"large":false}).appendPoint([149.5,-80.83]).appendArc([146.5,-77.83],{"radius":3,"clockwise":false,"large":false}).appendPoint([132.5,-77.83]).appendPoint([132.5,-67.23]).appendArc([129.5,-64.23],{"radius":3,"clockwise":false,"large":false}).appendPoint([115.5,-64.23]).appendPoint([115.5,-63.83]).appendArc([112.5,-60.83],{"radius":3,"clockwise":false,"large":false}).appendPoint([98.466058,-60.83]).appendArc([95.5,-58.28],{"radius":3,"clockwise":false,"large":false}).appendPoint([81.5,-58.28]).appendPoint([81.5,-57.03]).appendArc([78.5,-54.03],{"radius":3,"clockwise":false,"large":false}).appendPoint([59.5,-54.03]).appendArc([56.5,-57.03],{"radius":3,"clockwise":false,"large":false}).appendPoint([56.5,-65.25]).appendPoint([42.5,-65.25]).appendArc([39.5,-68.25],{"radius":3,"clockwise":false,"large":false}).appendPoint([39.5,-69.5]).appendPoint([25.5,-69.5]).appendArc([22.5,-72.5],{"radius":3,"clockwise":false,"large":false}).appendPoint([22.5,-142.5]).appendArc([25.5,-145.5],{"radius":3,"clockwise":false,"large":false}).close().innerToCAG()
.subtract(
    new CSG.Path2D([[27,-144],[41,-144]]).appendPoint([41,-153.75]).appendArc([44,-156.75],{"radius":3,"clockwise":false,"large":false}).appendPoint([60,-156.75]).appendArc([63,-153.75],{"radius":3,"clockwise":false,"large":false}).appendPoint([63,-145.53]).appendPoint([77,-145.53]).appendArc([80,-142.53],{"radius":3,"clockwise":false,"large":false}).appendPoint([80,-132.78]).appendPoint([92.033942,-132.78]).appendArc([95,-135.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([99.2677808,-135.33]).appendPoint([96.5579293,-150.6983321]).appendArc([98.9914081,-154.1736999],{"radius":3,"clockwise":false,"large":false}).appendPoint([114.7483321,-156.9520707]).appendArc([114.9180932,-156.9770215],{"radius":3,"clockwise":false,"large":false}).appendArc([115.0714646,-157.053954],{"radius":3,"clockwise":false,"large":false}).appendPoint([129.5723892,-163.8158462]).appendArc([129.9385037,-163.9581925],{"radius":3,"clockwise":false,"large":false}).appendArc([130.2651015,-164.1764493],{"radius":3,"clockwise":false,"large":false}).appendPoint([144.1215079,-172.1764493]).appendArc([148.2195841,-171.0783731],{"radius":3,"clockwise":false,"large":false}).appendPoint([156.2195841,-157.2219667]).appendArc([155.1215079,-153.1238905],{"radius":3,"clockwise":false,"large":false}).appendPoint([141.2651015,-145.1238905]).appendArc([139.9493024,-144.727627],{"radius":3,"clockwise":false,"large":false}).appendArc([138.869991,-143.8770748],{"radius":3,"clockwise":false,"large":false}).appendPoint([127.8320535,-138.73]).appendPoint([128,-138.73]).appendArc([131,-135.73],{"radius":3,"clockwise":false,"large":false}).appendPoint([131,-135.33]).appendPoint([145,-135.33]).appendArc([148,-132.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([148,-116.33]).appendArc([147.9580399,-115.83],{"radius":3,"clockwise":false,"large":false}).appendArc([148,-115.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([148,-99.33]).appendArc([147.9580399,-98.83],{"radius":3,"clockwise":false,"large":false}).appendArc([148,-98.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([148,-82.33]).appendArc([145,-79.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([131,-79.33]).appendPoint([131,-68.73]).appendArc([128,-65.73],{"radius":3,"clockwise":false,"large":false}).appendPoint([114,-65.73]).appendPoint([114,-65.33]).appendArc([111,-62.33],{"radius":3,"clockwise":false,"large":false}).appendPoint([96.966058,-62.33]).appendArc([94,-59.78],{"radius":3,"clockwise":false,"large":false}).appendPoint([80,-59.78]).appendPoint([80,-58.53]).appendArc([77,-55.53],{"radius":3,"clockwise":false,"large":false}).appendPoint([61,-55.53]).appendArc([58,-58.53],{"radius":3,"clockwise":false,"large":false}).appendPoint([58,-66.75]).appendPoint([44,-66.75]).appendArc([41,-69.75],{"radius":3,"clockwise":false,"large":false}).appendPoint([41,-71]).appendPoint([27,-71]).appendArc([24,-74],{"radius":3,"clockwise":false,"large":false}).appendPoint([24,-90]).appendArc([24.0419601,-90.5],{"radius":3,"clockwise":false,"large":false}).appendArc([24,-91],{"radius":3,"clockwise":false,"large":false}).appendPoint([24,-107]).appendArc([24.0419601,-107.5],{"radius":3,"clockwise":false,"large":false}).appendArc([24,-108],{"radius":3,"clockwise":false,"large":false}).appendPoint([24,-124]).appendArc([24.0419601,-124.5],{"radius":3,"clockwise":false,"large":false}).appendArc([24,-125],{"radius":3,"clockwise":false,"large":false}).appendPoint([24,-141]).appendArc([27,-144],{"radius":3,"clockwise":false,"large":false}).close().innerToCAG()
).extrude({ offset: [0, 0, 16] });
}


function l_case_3d_case_fn() {
    // creating part 0 of case l_case_3d
    let l_case_3d__part_0 = l_key_based_board_outline_with_extra_padding_extrude_3_outline_fn();

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
    let l_case_3d__part_1 = l_case_border_outline_extrude_16_outline_fn();

    // make sure that rotations are relative
    let l_case_3d__part_1_bounds = l_case_3d__part_1.getBounds();
    let l_case_3d__part_1_x = l_case_3d__part_1_bounds[0].x + (l_case_3d__part_1_bounds[1].x - l_case_3d__part_1_bounds[0].x) / 2
    let l_case_3d__part_1_y = l_case_3d__part_1_bounds[0].y + (l_case_3d__part_1_bounds[1].y - l_case_3d__part_1_bounds[0].y) / 2
    l_case_3d__part_1 = translate([-l_case_3d__part_1_x, -l_case_3d__part_1_y, 0], l_case_3d__part_1);
    l_case_3d__part_1 = rotate([0,0,0], l_case_3d__part_1);
    l_case_3d__part_1 = translate([l_case_3d__part_1_x, l_case_3d__part_1_y, 0], l_case_3d__part_1);

    l_case_3d__part_1 = translate([0,0,0], l_case_3d__part_1);
    result = result.union(l_case_3d__part_1);


    return result;
}

function addMarkerAboveModel(model) {
    const bounds = model.getBounds();
    const maxX = bounds[1].x;
    const maxY = bounds[1].y;
    const maxZ = bounds[1].z;

    const marker = cube({size: [10, 10, 10]});
    // Position the cube so its bottom is 30 units above maxZ
    // Also position it at maxX and maxY
    const markerPosition = [maxX, maxY, maxZ];
    const movedMarker = translate(markerPosition, marker);

    return model.union(movedMarker);
}

function debugBoundsMarkers(bounds) {
  const markers = [];

  // Min corner
  markers.push(translate([bounds[0].x, bounds[0].y, bounds[0].z], cube({size: 5, center: true})));

  // Max corner
  markers.push(translate([bounds[1].x, bounds[1].y, bounds[1].z], cube({size: 5, center: true})));

  return union(markers);
}

// function addMarkersOnLeftHalf(model) {
//   // 1. Get bounds and compute centerX
//   const bounds = model.getBounds();
//   const minX = bounds[0].x;
//   const maxX = bounds[1].x;
//   const centerX = minX + (maxX - minX) / 2;

//   // 2. Get all vertices
//   const polygons = model.toPolygons();
//   const markers = [];
//   const seen = new Set(); // to avoid duplicates

//   polygons.forEach(poly => {
//     poly.vertices.forEach(vertex => {
//       const pos = vertex.pos;
//       if (pos.x < centerX) {
//         // Avoid duplicate markers by rounding coords
//         const key = `${pos.x.toFixed(4)},${pos.y.toFixed(4)},${pos.z.toFixed(4)}`;
//         if (!seen.has(key)) {
//           seen.add(key);

//           // 3. Create marker (tiny cube), offset by +20 on Y
//           const marker = cube({size: 2, center: true});
//           const position = [pos.x, pos.y + 20, pos.z];
//           markers.push(translate(position, marker));
//         }
//       }
//     });
//   });

//   return union(model, ...markers);
// }

function addMarkersOnBottomYHalf(model) {
  // 1. Get bounds and compute centerY
  const bounds = model.getBounds();
  const minY = bounds[0].y;
  const maxY = bounds[1].y;
  const centerY = minY + (maxY - minY) / 2;

  // 2. Get all vertices
  const polygons = model.toPolygons();
  const markers = [];
  const seen = new Set(); // avoid duplicates

  polygons.forEach(poly => {
    poly.vertices.forEach(vertex => {
      const pos = vertex.pos;
      if (pos.y < centerY) {
        // Avoid duplicate markers
        const key = `${pos.x.toFixed(4)},${pos.y.toFixed(4)},${pos.z.toFixed(4)}`;
        if (!seen.has(key)) {
          seen.add(key);

          // 3. Create marker cube 1x1x1, center it
          const marker = cube({size: 1, center: true});
          const position = [pos.x, pos.y, pos.z + 20]; // move UP in Z
          markers.push(translate(position, marker));
        }
      }
    });
  });

  return union(model, ...markers);
}


function main() {
  const model = l_case_3d_case_fn();
  const result = addMarkersOnBottomYHalf(model);
  return result;
}



// function main() {
//   const model = l_case_3d_case_fn();
//   const result = addMarkersOnLeftHalf(model);
//   return result;
// }




// function main() {
//   const model = l_case_3d_case_fn();
//   const bounds = model.getBounds();
//   const boundsMarkers = debugBoundsMarkers(bounds);

//   return union(model, boundsMarkers);
// }



// function main() {
//     const model = l_case_3d_case_fn();
//     const modelWithMarker = addMarkerAboveModel(model);
//     return modelWithMarker;
// }


        