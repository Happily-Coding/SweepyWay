// version anterior comentada:

function main() {
  var width = 100;   // width of the handrest
  var height = 30;   // height at the tallest point (left)
  var depth = 10;    // extrusion depth (3D thickness)
  var curveSegments = 30; // how smooth the curve is

  // Bottom edge: starts at (0, 0) and goes to (width, 0)
  var bottomLeft = [0, 0];
  var bottomRight = [width, 0];

  // Curve: from top-left (0, height) to top-right (width, 0)
  // We'll approximate a downward sloping curve using cosine
  var curvePoints = [];
  for (var i = 0; i <= curveSegments; i++) {
    var t = i / curveSegments;
    var x = t * width;
    var y = height * Math.cos(t * Math.PI / 2); // from height to 0
    curvePoints.push([x, y]);
  }

  // Full 2D outline (go counterclockwise)
  var shapePoints = [
    bottomLeft,
    ...curvePoints,
    bottomRight
  ];

  var shape2D = polygon(shapePoints);
  return linear_extrude({ height: depth }, shape2D);
}

// This is cosine slope, but we could use a Bezier curve which allows us to define control points to better setup the slope.




//Apuntando correctamente:

function main() {
  var width = 100;
  var height = 30;
  var depth = 80;
  var curveSegments = 30;

  var curvePoints = [];
  for (var i = 0; i <= curveSegments; i++) {
    var t = i / curveSegments;
    var x = t * width;
    var y = height * Math.cos(t * Math.PI / 2);
    curvePoints.push([x, y]);
  }

  var shapePoints = [[0, 0], ...curvePoints, [width, 0]];
  var shape2D = polygon(shapePoints);

  return linear_extrude({ height: depth }, shape2D)
           .rotateX(90)
           .translate([0, 0, 0]);
}


