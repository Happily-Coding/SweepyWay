#!/bin/bash
for f in *.jscad; do
  echo "Converting $f..."
  openjscad "$f" -o "${f%.jscad}.stl"
done
