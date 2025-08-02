function main() {
  var keyboardLength = 50;       // Length of the keyboard
  var tentingAngle = 15;          // Tenting angle in degrees
  var tenting_column_offset = -10; // Offset from keyboard end
  var tenting_column_width = 10;   // Width of the support column
  var tenting_column_y_offset = -1

  var angleRad = tentingAngle * Math.PI / 180; // Convert angle to radians
  
  var tenting_column_x_start = keyboardLength + tenting_column_offset;
  var tenting_column_x_end = tenting_column_x_start + tenting_column_width;

  // Height at the end of the keyboard (the end of the sloped line)
  var keyboard_end_y = Math.tan(angleRad) * keyboardLength;

  // Y positions for the tenting column (top)
  var tenting_column_hstart_topy = Math.tan(angleRad) * tenting_column_x_start + tenting_column_y_offset 
  var tenting_column_hend_topy = Math.tan(angleRad) * tenting_column_x_end + tenting_column_y_offset

  // Y positions for the tenting column (bottom, flat on table)
  var tenting_column_hstart_boty = 0;
  var tenting_column_hend_boty = 0;

  // Create the sloped line representing the keyboard (for reference)
  var path = new CSG.Path2D([[0, 0], [keyboardLength, keyboard_end_y]]);
  var lineShape = path.rectangularExtrude(0.5, 1, 1);

  // Create the tenting support column as a polygon
  var tentingColumn2D = polygon([
    [tenting_column_x_start, tenting_column_hstart_topy], // top-left
    [tenting_column_x_end, tenting_column_hend_topy],     // top-right
    [tenting_column_x_end, tenting_column_hend_boty],     // bottom-right
    [tenting_column_x_start, tenting_column_hstart_boty]  // bottom-left
  ]);

  var tentingColumn3D = linear_extrude({ height: 10 }, tentingColumn2D);

  // Return both shapes together
  return union(lineShape, tentingColumn3D);
}
