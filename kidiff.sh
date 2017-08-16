#!/usr/bin/env bash

# Takes one or two git ref's as arguments and generates visual diffs between them
# If only one ref specified, generates a diff from that file
# If no refs specified, assumes HEAD

OUTPUT_DIR="./plots"

#export PYTHONPATH=/Applications/Kicad/kicad.app/Contents/Frameworks/python/site-packages/:$PATH
# Find .kicad_files that differ between commits
###############################################

## Look at number of arguments provided set different variables based on number of git refs
## User provided no git references, compare against last git commit
qual="100"
if [ $# -eq 0 ]; then
    DIFF_1="current"
    DIFF_2=$(fossil info current | grep ^uuid: | sed 's/uuid:         //g' | cut -c 1-6)
    echo $DIFF_2
#    CHANGED_KICAD_FILES=$(git diff --name-only "$DIFF_2" | grep '.kicad_pcb')
# Might need to use strategy here to cope with spaces in name
#4     sh -c {find . -name "*.pro" -print0 | xargs -0 gsed -E -i.bkp 's/update=.*/update=Date/'}
    CHANGED_KICAD_FILES=$(fossil diff --brief -r  "$DIFF_2" | grep '.kicad_pcb$' | sed 's/^CHANGED  //g; s/^ADDED    //g')
    if [[ -z "$CHANGED_KICAD_FILES" ]]; then echo "No .kicad_pcb files differ" && exit 0; fi
    # Copy all modified kicad_file to $OUTPUT_DIR/current
    for k in $CHANGED_KICAD_FILES; do
        mkdir -p "$OUTPUT_DIR/$DIFF_1"
        cp "$k" $OUTPUT_DIR/current
    done
    # Copy the specified git commit kicad_file to $OUTPUT_DIR/$(git ref)
    for k in $CHANGED_KICAD_FILES; do
        mkdir -p "$OUTPUT_DIR/$DIFF_2"
        echo "Copying $DIFF_2:$k to $OUTPUT_DIR/$DIFF_2/"
        fossil cat $k -r $DIFF_2 > "$OUTPUT_DIR/$DIFF_2/$(basename $k)"
    done
## User provided 1 git reference to compare against current files
elif [ $# -eq 1 ]; then
    DIFF_1="current"
    DIFF_2="$1"
    CHANGED_KICAD_FILES=$(fossil diff --brief -r  "$DIFF_2" | grep '.kicad_pcb$' | sed 's/^CHANGED  //g; s/^ADDED    //g')
    if [[ -z "$CHANGED_KICAD_FILES" ]]; then echo "No .kicad_pcb files differ" && exit 0; fi
    # Copy all modified kicad_file to $OUTPUT_DIR/current
    for k in $CHANGED_KICAD_FILES; do
        mkdir -p "$OUTPUT_DIR/$DIFF_1"
        cp "$k" $OUTPUT_DIR/current
    done
    # Copy the specified git commit kicad_file to $OUTPUT_DIR/$(git ref)
    for k in $CHANGED_KICAD_FILES; do
        mkdir -p "$OUTPUT_DIR/$DIFF_2"
        echo "Copying $DIFF_2:$k to $OUTPUT_DIR/$DIFF_2/$k"
        fossil cat $k -r $DIFF_2  > "$OUTPUT_DIR/$DIFF_2/$(basename $k)"
    done
## User provided 2 git references to compare
elif [ $# -eq 2 ]; then
    DIFF_1="$1"
    DIFF_2="$2"
    CHANGED_KICAD_FILES=$(git diff --name-only "$DIFF_1" "$DIFF_2" | grep '.kicad_pcb')
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
## User provided too many git referencess
else
    echo "Please only provide 1 or 2 arguments: not $#"
    exit 2
fi

echo "Kicad files saved to:  '$OUTPUT_DIR/$DIFF_1' and '$OUTPUT_DIR/$DIFF_2'"

# Generate png files from kicad output
#######################################
#curl -s https://gist.githubusercontent.com/spuder/4a76e42f058ef7b467d9/raw -o /tmp/plot_board.py
#chmod +x /tmp/plot_board.py

#I have fond the simplest way to achieve this is to save the files as SVG and use rsvg-conver to produce the .png files

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

p.sans {
    font-family: Arial, Helvetica, sans-serif;
}

p.mono {
    font-family: Courier, monospaced;
}
h1  {
    color: #0000ff;
}
.nobr {
    white-space: nowrap
}

</style>

</head>
<body>
<p class="sans">
<h1>PCBnew Graphical Diff</h1></p>
<p class="mono">
<h4>
<td class=nobr>Items in <p style="color:green;">GREEN</p> are in $DIFF_1 and not in $DIFF_2</td><br>
<td class=nobr>Items in <p style="color:red;">RED</p> are in $DIFF_2 and not in $DIFF_1</td><br>
<h/4>
</p>

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

cat >> $OUTPUT_DIR/tryptych/$(basename $g).html <<HTML
<!DOCTYPE HTML>
<html lang="en">
<head>
<style>
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

</style>
</head>

<h2>$base</h2>



<body>
<div class="responsive">
  <div class="gallery">
    <a target="_blank" href = $(basename $g).html>
      <a href= ../$DIFF_1/$(basename $g)><img src = "../$DIFF_1/$(basename $g)" width=500></a>
    </a>
    <div class="desc">$DIFF_1</div>
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
    <div class="desc">$DIFF_2</div>
  </div>
</div>
HTML
done

cat >>$OUTPUT_DIR/index.html<<FOOT
<div class="clearfix"></div>
<div style="padding:6px;">
<p>Graphical diffs of Kicad PCB (pcbnew) files.</p>
<p></p>
</div>
FOOT
echo "HTML created and written to index.html"
open $OUTPUT_DIR/index.html
