#!/usr/bin/env bash

# Takes one or two Fossil ref's as arguments and generates visual diffs between them
# If only one ref specified, generates a diff from that file
# If no refs specified, assumes HEAD

# TODO Consider moving all formatting to a single external css file.
# TODO Improve 3-pane layout - possible two side by side and comparison image underneath.
# TODO Add commandline quality option - Quality is dpi. 100 is fast but low quality 300 is a good compromise.
# TODO Improve sed removal of the the 'ADDED' 'CHANGED' tags. There is a difference in number of spaces in diffs with
# one vs two arguments. Need to match any number of spaces.
# Something like tr -d 'CHANGED[:space:]||ADDED[:space:]'
# TODO Remove filename from display format i.e 'filename-F_Cu' becomes 'F_Cu'
OUTPUT_DIR="./plots"
# TODO Have added this temprarily to simply remove all the plots prior to generating files.
# Theoretically the script could check if the files have already been generated and then only generate the
# missing files. This would permit multiple diff compares and you could also use an external diff tool like p4merge
# but the disadvantage is that the resoultions have to match. It is also more complicated to script
# Ideally one could request random compares within the web interface and there would
# be 'on the fly' svg/png creation and diff showing.


rm -r $OUTPUT_DIR
# Find .kicad_files that differ between commits
###############################################

## Look at number of arguments provided set different variables based on number of fossil refs
## User provided no Fossil references, compare against last Fossil commit
qual="300"
if [ $# -eq 0 ]; then
    DIFF_1="current"
    DIFF_2=$(fossil info current | grep ^uuid: | sed 's/uuid:         //g' | cut -c 1-6)
    echo $DIFF_2

# TODO Might need to use strategy here to cope with spaces in name
# using some varient of sh -c {find . -name "*.pro" -print0 | xargs -0 gsed -E -i.bkp 's/update=.*/update=Date/'}
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
        echo "Copying $DIFF_2:$k to $OUTPUT_DIR/$DIFF_2/"
        fossil cat $k -r $DIFF_2 > "$OUTPUT_DIR/$DIFF_2/$(basename $k)"
    done
## User provided 1 Fossil reference to compare against current files
elif [ $# -eq 1 ]; then
    DIFF_1="current"
    DIFF_2="$1"
    #CHANGED_KICAD_FILES=$(fossil diff --brief -r  "$DIFF_2" | grep '.kicad_pcb$' | sed 's/^CHANGED  //g; s/^ADDED    //g')
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
## User provided 2 Fossil references to compare
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
    # Copy the specified git commit kicad_file to $OUTPUT_DIR/$(git ref)
    for k in $CHANGED_KICAD_FILES; do
        mkdir -p "$OUTPUT_DIR/$DIFF_2"
        echo "Copying $DIFF_2:$k to $OUTPUT_DIR/$DIFF_2/$k"
        fossil cat $k -r $DIFF_2 > "$OUTPUT_DIR/$DIFF_2/$(basename $k)"
    done
## User provided too many referencess
else
    echo "Please only provide 1 or 2 arguments: not $#"
    exit 2
fi

echo "Kicad files saved to:  '$OUTPUT_DIR/$DIFF_1' and '$OUTPUT_DIR/$DIFF_2'"

# Generate png files from kicad output
#######################################
#curl -s https://gist.githubusercontent.com/spuder/4a76e42f058ef7b467d9/raw -o /tmp/plot_board.py
#chmod +x /tmp/plot_board.py

#I have found the simplest way to achieve this is to save the files as SVG and use rsvg-conver to produce the .png files

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

#TODO Use xargs or parallel to speed up
for p in /tmp/svg/$DIFF_1/*.svg; do
    d="$(basename $p)"
    echo "Converting $p to .png"
    #echo "Output_Dir "$OUTPUT_DIR
    #echo "Diff_1_dir" $DIFF_1
    #rsvg-convert -z 5 "$p" > "$OUTPUT_DIR/$DIFF_1/${d%%.*}.png"
    convert -density $qual -fuzz 1% -trim +repage "$p" "$OUTPUT_DIR/$DIFF_1/${d%%.*}.png"
done

#TODO Use xargs or parallel to speed up
for p in /tmp/svg/$DIFF_2/*.svg; do
    d="$(basename $p)"
    echo "Converting $p to .png"
#    pdftoppm -png -r 600 "$p" "$OUTPUT_DIR/$DIFF_2/${d%%.*}"
#    rsvg-convert "$p" -d 300 -z 5 > "$OUTPUT_DIR/$DIFF_2/${d%%.*}"
#    rsvg-convert -z 5 "$p" > "$OUTPUT_DIR/$DIFF_2/${d%%.*}.png"
    convert -density $qual -fuzz 1% -trim +repage "$p" "$OUTPUT_DIR/$DIFF_2/${d%%.*}.png"

done


# Generate png diffs
####################
#TODO Use xargs or parallel to speed up
for g in $OUTPUT_DIR/$DIFF_1/*.png; do
    mkdir -p "$OUTPUT_DIR/diff-$DIFF_1-$DIFF_2"
    echo "Generating composite image $OUTPUT_DIR/diff-$DIFF_1-$DIFF_2/$(basename $g)"
    #composite -stereo 0 -density 600 $OUTPUT_DIR/$DIFF_1/$(basename $g) $OUTPUT_DIR/$DIFF_2/$(basename $g) $OUTPUT_DIR/diff-$DIFF_1-$DIFF_2/$(basename $g)
    #convert $OUTPUT_DIR/diff-$DIFF_1-$DIFF_2/$(basename $g) -trim -density 600 -fill grey -opaque black $OUTPUT_DIR/diff-$DIFF_1-$DIFF_2/$(basename $g)
    convert '(' $OUTPUT_DIR/$DIFF_1/$(basename $g) -flatten -grayscale Rec709Luminance ')' \
        '(' $OUTPUT_DIR/$DIFF_2/$(basename $g) -flatten -grayscale Rec709Luminance ')' \
        '(' -clone 0-1 -compose darken -composite ')' \
        -channel RGB -combine $OUTPUT_DIR/diff-$DIFF_1-$DIFF_2/$(basename $g)
done


if [ -e $OUTPUT_DIR/index.html ]
        then echo "An index.html file already exists. Remove it to regenerate"
        exit
fi

if [ -d thumbs ]
        then echo "'thumbs' directory found"
else mkdir $OUTPUT_DIR/thumbs && echo "'thumbs' directory created"
fi

if [ -d tryptych ]
        then echo "'tryptych' directory found"
else mkdir $OUTPUT_DIR/tryptych && echo "'tryptych' directory created"
fi

cat >> $OUTPUT_DIR/index.html <<HEAD
<!DOCTYPE HTML>
<html lang="en">
<head>
<style>
body {
    background-color: #a2b1c6;
}
div.gallery {
    border: 1px solid #ccc;
}

div.gallery:hover {
    border: 1px solid #777;
}

div.gallery img {
    width: 100%;
    height: auto;
}

div.desc {
    padding: 15px;
    text-align: center;
    font: 25px arial, sans-serif;
}

* {
    box-sizing: border-box;
}

.responsive {
    padding: 0 6px;
    float: left;
    width: 24.99999%;
}

@media only screen and (max-width: 700px){
    .responsive {
        width: 49.99999%;
        margin: 6px 0;
    }
}

@media only screen and (max-width: 500px){
    .responsive {
        width: 100%;
    }
}

.clearfix:after {
    content: "";
    display: table;
    clear: both;
}

div.desc {
    padding: 15px;
    text-align: center;
    font: 20px arial, sans-serif;
}
div.desc1 {
    padding: 15px;
    text-align: left;
    align: middle;
    font: 20px arial, sans-serif;
    color: #FFFFFF;
}
div.desc2 {
    padding: 15px;
    text-align: left;
    font: 20px arial, sans-serif;
    color: #FFFFFF;
}
div.title {
    padding: 15px;
    text-align: left;
    font: 30px arial, sans-serif;
    color: #496075;
}
.box {
  float: left;
  width: 20px;
  height: 20px;
  margin: 5px;
  border-radius: 50%;
  border: 1px solid rgba(0, 0, 0, .2);
}

.red {
  background: #F40008;
}

.green {
  background: #43ff01;
}



</style>

</head>
<body>
<div class="title">
PCBnew Graphical Diff</div>

<div class="box green"></div><div class="desc1">in <b>$DIFF_1</b> and not in <b>$DIFF_2</b></div>
<div class="box red"></div><div class="desc2">in <b>$DIFF_2</b> and not in <b>$DIFF_1</b></div>


HEAD

#for g in $OUTPUT_DIR/diff-$DIFF_1-$DIFF_2/$HTTP/*.png; do
for g in $OUTPUT_DIR/diff-$DIFF_1-$DIFF_2/*.png; do
#convert $g -fuzz 1% -trim +repage $g
#convert -resize x250 $(basename $g) thumbs/th_$(basename $g)

cp  $g ./plots/thumbs/th_$(basename $g)
route=$g
file=${route##*/}
base=${file%.*}
dir=$(dirname $g)

echo $dir


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
#Need to adjsut the width of the TRYPTYCH view so it is bigger (and maybe dif underneath?)
cat >> $OUTPUT_DIR/tryptych/$(basename $g).html <<HTML
<!DOCTYPE HTML>
<html lang="en">
<head>
<style>
body {
    background-color: #a2b1c6;
}
div.gallery {
    border: 1px solid #ccc;
}

div.gallery:hover {
    border: 1px solid #777;
}

div.gallery img {
    width: 100%;
    height: auto;
}

div.desc {
    padding: 15px;
    text-align: center;
    font: 20px arial, sans-serif;
    background: #ffffff;
}
div.desc1 {
    padding: 15px;
    text-align: center;
    font: 20px arial, sans-serif;
    background: #43FF01;
}
div.desc2 {
    padding: 15px;
    text-align: center;
    font: 20px arial, sans-serif;
    background: #F40008;
}
div.title {
    padding: 15px;
    text-align: left;
    font: 30px arial, sans-serif;
    color: #496075;
}
* {
    box-sizing: border-box;
}

.responsive {
    padding: 0 6px;
    float: left;
    width: 33.332%;
}

@media only screen and (max-width: 700px){
    .responsive {
        width: 49.99999%;
        margin: 6px 0;
    }
}

@media only screen and (max-width: 500px){
    .responsive {
        width: 100%;
    }
}

.clearfix:after {
    content: "";
    display: table;
    clear: both;
}


</style>
</head>

<div class="title">$base</div>

<body>
<div class="responsive">
  <div class="gallery">
    <a target="_blank" href = $(basename $g).html>
      <a href= ../$DIFF_1/$(basename $g)><img src = "../$DIFF_1/$(basename $g)" width=500></a>
    </a>
    <div class="desc1">$DIFF_1</div>
  </div>
</div>
<div class="responsive">
  <div class="gallery">
    <a target="_blank" href = $(basename $g).html>
      <a href = ../diff-$DIFF_1-$DIFF_2/$(basename $g) ><img src = ../diff-$DIFF_1-$DIFF_2/$(basename $g) width=500></a>
    </a>
    <div class="desc">Composite</div>
  </div>
</div>
<div class="responsive">
  <div class="gallery">
    <a target="_blank" href = $(basename $g).html>
      <a href= ../$DIFF_2/$(basename $g)> <img src = "../$DIFF_2/$(basename $g)" width=500></a>
    </a>
    <div class="desc2">$DIFF_2</div>
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
