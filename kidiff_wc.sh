#!/usr/bin/env bash

# Takes one or two Fossil ref's as arguments and generates visual diffs between them
# If only one ref specified, generates a diff from that file
# If no refs specified, assumes CURRENT

# TODO Consider moving all formatting to a single, external css file and putting all
# created web content into a 'web' directory.

# TODO Improve 3-pane layout - possible two side by side and comparison image underneath?

# TODO Remove filename from display format i.e 'filename-F_Cu' becomes 'F_Cu'

qual="100"
# TODO Add command line quality option - Quality is dpi. 100 is fast but low quality
# 600 is very detailed. 300 is a good compromise.

# TODO Add recolour option
# 952927
# convert F_Cu.png -fill "#952927" -fuzz 75% -opaque "#ffffff" test2.png

# Remove old plot files
rm -r /tmp/svg

# Set directory for plotting
OUTPUT_DIR="./plots"
rm -r $OUTPUT_DIR
mkdir $OUTPUT_DIR

# TODO Have added this temporarily to simply remove all the plots prior to generating files.
# Theoretically the script could check if the files have already been generated and then only generate the
# missing files. This would permit multiple diff compares and you could also use an external diff tool like p4merge
# but the disadvantage is that the resoultions have to match. It is also more complicated to script
# Ideally one could request random compares within the web interface and there would
# be 'on the fly' svg/png creation and diff showing.

# Try to keep the web components seperate from the images so that the images could be
# looked at using a graphical diff viewer like p4merge.
# Set directory for web backend

WEB_DIR=$OUTPUT_DIR"/web"
mkdir $WEB_DIR
cp ~/Kicad/KiCad-Diff/style.css $WEB_DIR/

# TODO Might need to use a more complex strategy  to cope with spaces in filename
# using some varient of 'find . -name "*.pro" -print0 | xargs -0'

#################################
# Colours to substitute per layer
#
# Additionally need to add vias, and internal layers.
# TODO Parse the pcbnew file to determine which layers are active.

F_Cu="#952927"
B_Cu="#359632"
B_Paste="#3DC9C9"
F_Paste="#969696"
F_SilkS="#339697"
B_SilkS="#481649"
B_Mask="#943197"
F_Mask="#943197"
Edge_Cuts="#C9C83B"
In1_Cu="#C2C200"
In2_Cu="#C200C2"
User_Dwgs="#C2C2C2"
User_Cmts="#000085"
User_Eco1="#008500"
User_Eco2="#C2C200"
B_Fab="#858585"
F_Fab="#C2C200"


# These are the colour definitions for the 'solarised' theme from pcbnew.
#ColorPCBLayer_F.Cu=rgb(221, 47, 44)
#ColorPCBLayer_In3.Cu=rgba(194, 194, 194, 0.800)
#ColorPCBLayer_In4.Cu=rgba(0, 132, 132, 0.800)
#ColorPCBLayer_In5.Cu=rgba(0, 132, 0, 0.800)
#ColorPCBLayer_In6.Cu=rgba(0, 0, 132, 0.800)
#ColorPCBLayer_Margin=rgba(194, 0, 194, 0.800)
#ColorPCBLayer_B.CrtYd=rgba(194, 194, 0, 0.800)
#ColorPCBLayer_F.CrtYd=rgba(132, 132, 132, 0.800)
#ColorTxtFrontEx=rgba(194, 194, 194, 0.800)
#ColorTxtBackEx=rgba(0, 0, 132, 0.800)
#ColorTxtInvisEx=rgba(132, 132, 132, 0.800)
#ColorAnchorEx=rgba(0, 0, 132, 0.800)
#ColorPadBackEx=rgba(0, 132, 0, 0.800)
#ColorPadFrontEx=rgba(132, 132, 132, 0.800)
#ColorViaThruEx=rgba(194, 194, 194, 0.800)
#ColorViaBBlindEx=rgba(132, 132, 0, 0.800)
#ColorViaMicroEx=rgba(0, 132, 132, 0.800)
#ColorNonPlatedEx=rgba(194, 194, 0, 0.800)



#########################################################
# Find the .kicad_pcb files that differ between commits #
#########################################################

# Look at number of arguments provided set different variables based on number of Fossil refs
#############################################################################################

# 0. User provided no Fossil references, compare against last Fossil commit

if [ $# -eq 0 ]; then
  DIFF_1="current"
  DIFF_2=$(fossil info current | grep ^uuid: | tr -d 'uuid:[:space:]' | cut -c 1-6)
  echo $DIFF_2
  CHANGED_KICAD_FILES=$(fossil diff --brief -r  "$DIFF_2" | grep '.kicad_pcb$' | tr -d 'CHANGED[:space:]||ADDED[:space:]')
  if [[ -z "$CHANGED_KICAD_FILES" ]]; then echo "No .kicad_pcb files differ" && exit 0; fi

  # Copy all modified kicad_pcb files to $OUTPUT_DIR/current

  for k in $CHANGED_KICAD_FILES; do
    mkdir -p "$OUTPUT_DIR/$DIFF_1"
    cp "$k" $OUTPUT_DIR/current
  done

  # Copy the  Fossil commit kicad_pcb file to $OUTPUT_DIR/commit uuid

  for k in $CHANGED_KICAD_FILES; do
    mkdir -p "$OUTPUT_DIR/$DIFF_2"
    echo "Copying $DIFF_2:$k to $OUTPUT_DIR/$DIFF_2/"
    fossil cat $k -r $DIFF_2 > "$OUTPUT_DIR/$DIFF_2/$(basename $k)"
  done


  # 1. User supplied one Fossil reference to compare against current files

  elif [ $# -eq 1 ]; then
  DIFF_1="current"
  DIFF_2="$1"
  CHANGED_KICAD_FILES=$(fossil diff --brief -r  "$DIFF_2" | grep '.kicad_pcb$' | tr -d 'CHANGED[:space:]||ADDED[:space:]')
  if [[ -z "$CHANGED_KICAD_FILES" ]]; then echo "No .kicad_pcb files differ" && exit 0; fi

  # Copy all modified kicad_file to $OUTPUT_DIR/current

  for k in $CHANGED_KICAD_FILES; do
    mkdir -p "$OUTPUT_DIR/$DIFF_1"
    cp "$k" $OUTPUT_DIR/current
  done

  # Copy the specified Fossil commit kicad_file to $OUTPUT_DIR/$(Fossil ref)

  for k in $CHANGED_KICAD_FILES; do
    mkdir -p "$OUTPUT_DIR/$DIFF_2"
    echo "Copying $DIFF_2:$k to $OUTPUT_DIR/$DIFF_2/$k"
    fossil cat $k -r $DIFF_2  > "$OUTPUT_DIR/$DIFF_2/$(basename $k)"
  done

  # 2. User supplied 2 Fossil references to compare

  elif [ $# -eq 2 ]; then
  DIFF_1="$1"
  DIFF_2="$2"
  CHANGED_KICAD_FILES=$(fossil diff --brief -r "$DIFF_1" --to "$DIFF_2" | grep '.kicad_pcb' | tr -d 'CHANGED[:space:]||ADDED[:space:]')
  if [[ -z "$CHANGED_KICAD_FILES" ]]; then echo "No .kicad_pcb files differ" && exit 0; fi

  # Copy all modified kicad_file to $OUTPUT_DIR/current

  for k in $CHANGED_KICAD_FILES; do
    mkdir -p "$OUTPUT_DIR/$DIFF_1"
    fossil cat $k -r $DIFF_1  > "$OUTPUT_DIR/$DIFF_1/$(basename $k)"
  done

  # Copy the specified Fossil commit kicad_file to $OUTPUT_DIR/Fossil uuid

  for k in $CHANGED_KICAD_FILES; do
    mkdir -p "$OUTPUT_DIR/$DIFF_2"
    echo "Copying $DIFF_2:$k to $OUTPUT_DIR/$DIFF_2/$k"
    fossil cat $k -r $DIFF_2 > "$OUTPUT_DIR/$DIFF_2/$(basename $k)"
  done


  # 3. User provided too many references

else
  echo "Please only provide 1 or 2 arguments: not $#"
  exit 2
fi

echo "Kicad files saved to:  '$OUTPUT_DIR/$DIFF_1' and '$OUTPUT_DIR/$DIFF_2'"

# Generate svg files from kicad output
######################################
#
# Use the python script 'plot_pcbnew.py' to generate svg files from the two *.kicad_pcb files.
# Files are saved in /tmp/svg/COMMIT_ID
#

for f in $OUTPUT_DIR/$DIFF_1/*.kicad_pcb; do
  mkdir -p /tmp/svg/$DIFF_1
  echo "Converting $f to .svg:  Files will be saved to /tmp/svg"
  /usr/local/bin/plot_pcbnew.py "$f" "/tmp/svg/$DIFF_1"
done

for f in $OUTPUT_DIR/$DIFF_2/*.kicad_pcb; do
  mkdir -p /tmp/svg/$DIFF_2
  echo "Converting $f to .svg's Files will be saved to /tmp/svg"
  /usr/local/bin/plot_pcbnew.py "$f" "/tmp/svg/$DIFF_2"
done

# Convert svg files into png
######################################
#
# Parse the svg files in /tmp/svg/COMMIT_ID using Image Magick.
# The conversion trims the image to the active area using the 'trim' function.
# Fuzz is probably not nescessary (trim measures the corner pixel value and trims
# to the first non-corner coloured pixel. Fuzz allows for minor variation but as this is
# a generated svg, pixels should be white.)
#
# The .png files are created in the output directory.


for p in /tmp/svg/$DIFF_1/*.svg; do
  d=$(basename $p)
  echo "Converting $p to .png"
  convert -density $qual -fuzz 1% -trim +repage "$p" "$OUTPUT_DIR/$DIFF_1/${d%%.*}.png"
  convert "$OUTPUT_DIR/$DIFF_1/${d%%.*}.png" -negate "$OUTPUT_DIR/$DIFF_1/${d%%.*}.png"
done



for p in /tmp/svg/$DIFF_2/*.svg; do
  d=$(basename $p)
  echo "Converting $p to .png"
  convert -density $qual -fuzz 1% -trim +repage "$p" "$OUTPUT_DIR/$DIFF_2/${d%%.*}.png"
  convert "$OUTPUT_DIR/$DIFF_2/${d%%.*}.png" -negate "$OUTPUT_DIR/$DIFF_2/${d%%.*}.png"
done


# Generate png diffs between DIFF_1 and DIFF_2
##############################################
#
# Originally the intention was to use the ImageMagic 'composite stereo 0' function to identify
# where items have moved but I could not get this to work.
# This flattens the original files to greyscale and they need to be converted
# back to rgb in order to be colourised.

for g in $OUTPUT_DIR/$DIFF_1/*.png; do
  d=$(basename $g)
  y=${d%.png}
  layerName=${y##*-}
  mkdir -p "$OUTPUT_DIR/diff-$DIFF_1-$DIFF_2"
  echo "Generating composite image $OUTPUT_DIR/diff-$DIFF_1-$DIFF_2/$(basename $g)"
  convert '(' $OUTPUT_DIR/$DIFF_2/$(basename $g) -flatten -grayscale Rec709Luminance ')' \
          '(' $OUTPUT_DIR/$DIFF_1/$(basename $g) -flatten -grayscale Rec709Luminance ')' \
          '(' -clone 0-1 -compose darken -composite ')' \
          -channel RGB -combine $OUTPUT_DIR/diff-$DIFF_1-$DIFF_2/$(basename $g)
  convert "$OUTPUT_DIR/diff-$DIFF_1-$DIFF_2/$(basename $g)" -fill ${!layerName} -fuzz 75% -opaque "#ffffff" "$OUTPUT_DIR/diff-$DIFF_1-$DIFF_2/$(basename $g)"
done

for p in $OUTPUT_DIR/$DIFF_1/*.png; do
  d=$(basename $p)
  y=${d%.png}
  layerName=${y##*-}
  echo "Converting $layerName to .png with colour "${!layerName}
  convert "$OUTPUT_DIR/$DIFF_1/${d%%.*}.png" -define png:color-type=2 "$OUTPUT_DIR/$DIFF_1/${d%%.*}.png"
  convert "$OUTPUT_DIR/$DIFF_1/${d%%.*}.png" -fill ${!layerName} -fuzz 75% -opaque "#ffffff" "$OUTPUT_DIR/$DIFF_1/${d%%.*}.png"
done


for p in $OUTPUT_DIR/$DIFF_2/*.png; do
  d=$(basename $p)
  y=${d%.png}
  layerName=${y##*-}
  echo "Converting $layerName to .png with colour "${!layerName}
  convert "$OUTPUT_DIR/$DIFF_2/${d%%.*}.png" -define png:color-type=2 "$OUTPUT_DIR/$DIFF_2/${d%%.*}.png"
  convert "$OUTPUT_DIR/$DIFF_2/${d%%.*}.png" -fill ${!layerName} -fuzz 75% -opaque "#ffffff" "$OUTPUT_DIR/$DIFF_2/${d%%.*}.png"
done

# Setup web directories for web output
######################################
#
# Remove index.html prior to streaming new data
# TODO Would be neater to put thumbs, tryptych, index and any .css sheet in a 'web' directory
#

if [ -e $OUTPUT_DIR/index.html ]
    then rm $OUTPUT_DIR/index.html
fi

if [ -d thumbs ]
then echo "'thumbs' directory found"
else mkdir $OUTPUT_DIR/thumbs && echo "'thumbs' directory created"
fi

if [ -d tryptych ]
then echo "'tryptych' directory found"
else mkdir $OUTPUT_DIR/tryptych && echo "'tryptych' directory created"
fi

# Stream HTML <head> and <style> to index.html
##############################################
#
# It would make more sense to stream this to $OUTPUT_DIR/web/style.css
# and reuse it in the 'tryptich' section.

cat >> $OUTPUT_DIR/index.html <<HEAD
<!DOCTYPE HTML>
<html lang="en">
<head>
<link rel="stylesheet" type="text/css" href="web/style.css" media="screen" />
</head>

<body>
<div class="title">
PCBnew Graphical Diff</div>
<div class="box green"></div><div class="subtitle">ADDED i.e. in <b>$DIFF_1</b> and not in <b>$DIFF_2</b></div>
<div class="box red"></div><div class="subtitle">REMOVED i.e. in <b>$DIFF_2</b> and not in <b>$DIFF_1</b></div>
HEAD

for g in $OUTPUT_DIR/diff-$DIFF_1-$DIFF_2/*.png; do
convert -resize 300 $g ./plots/thumbs/th_$(basename $g)
#cp  $g ./plots/thumbs/th_$(basename $g)

  route=$g
  file=${route##*/}
  base=${file%.*}
#  dir=$(dirname $g)
#  echo $dir

cat >> $OUTPUT_DIR/index.html <<HTML
<div class="responsive">
  <div class="gallery">
    <a target="_blank" href = tryptych/$(basename $g).html>
      <img src = thumbs/th_$(basename $g) width="300" height="200">
    </a>
    <div class="desc">$base</div>
  </div>
</div>
HTML


cat >> $OUTPUT_DIR/tryptych/$(basename $g).html <<HTML
<!DOCTYPE HTML>
<html lang="en">
<head>
<link rel="stylesheet" type="text/css" href="../web/style.css" media="screen" />
</head>

<div class="title">$base</div>

<body>

<div class="responsive">
    <div class="gallery">
        <a target="_blank" href = $(basename $g).html>
            <a href= ../$DIFF_1/$(basename $g)><img src = "../$DIFF_1/$(basename $g)" width=500></a>
        </a>
        <div class="desc green">$DIFF_1</div>
    </div>
</div>

<div class="responsive">
    <div class="gallery">
        <a target="_blank" href = $(basename $g).html>
            <a href = ../diff-$DIFF_1-$DIFF_2/$(basename $g) ><img src = ../diff-$DIFF_1-$DIFF_2/$(basename $g) width=500></a>
        </a>
        <div class="desc white">Composite</div>
    </div>
</div>

<div class="responsive">
  <div class="gallery">
      <a target="_blank" href = $(basename $g).html>
          <a href= ../$DIFF_2/$(basename $g)> <img src = "../$DIFF_2/$(basename $g)" width=500></a>
      </a>
      <div class="desc red">$DIFF_2</div>
  </div>
</div>
HTML

done

cat >>$OUTPUT_DIR/index.html<<FOOT
<div class="clearfix"></div>
<div style="padding:6px;">
</div>
FOOT
echo "HTML created and written to index.html"
open $OUTPUT_DIR/index.html
