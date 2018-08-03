#!/bin/bash
set -e

if [ "$#" -lt 4 ]; then
  echo "Usage: $0 <IMAGE_WIDTH> <IMAGE_PADDING> <INPUT_FOLDER> <OUTPUT_FOLDER>" >&2
  exit 1
fi

image_width=$1
padding=$2
input_folder=$3
output_folder=$4/$image_width
skip_svg_fix=$5

if [ "$skip_svg_fix" == "" ]; then
  echo "Removing some paths and polygons from SVGs..."
  find $input_folder/*.svg -exec sed -i -z 's/<path\s*clip[^<]*\/>//g' {} +
  find $input_folder/*.svg -exec sed -i -z 's/<polygon\s*clip[^<]*\/>//g' {} +
  echo "Done removing some paths and polygons from SVGs"
fi

rm -fr $output_folder
mkdir -p $output_folder

echo "Converting files from SVG to PNG..."
shopt -s extglob # to enable bash string manipulation for ${001##+(0)} below to work
for input_file in $input_folder/*.svg
do
  # generate output file name from the input file name
  output_file=`basename $input_file .svg`
  # remove leading zeros from the output file name
  output_file=${output_file##+(0)}
	echo "-e $output_folder/$output_file.png -w $image_width --export-area-drawing $input_file"
done | inkscape --shell | grep Bitmap
shopt -u extglob # disable again
echo "Done converting files from SVG to PNG"

echo "Adjusting padding for PNG files..."
cd $output_folder
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent *.png

# continue even if any command below fails, some files may not be there
set +e

mogrify -bordercolor transparent -border 0x$(($padding)) -background transparent -extent -0-$(($padding/2)) 1.png
mogrify -bordercolor transparent -border 0x$(($padding)) -background transparent -extent -0-$(($padding/2)) 2.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 50.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0+$(($padding/2)) 76.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 77.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 128.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 151.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 177.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 187.png
mogrify -bordercolor transparent -border 0x$(($padding/4)) -background transparent -extent -0-$(($padding/4)) 190.png
mogrify -bordercolor transparent -border 0x$(($padding/4)) -background transparent -extent -0-$(($padding/4)) 205.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0+$(($padding/2)) 207.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 208.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 249.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 262.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 282.png
mogrify -bordercolor transparent -border 0x$(($padding/4)) -background transparent -extent -0-$(($padding/4)) 301.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 305.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 322.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0+$(($padding/2)) 331.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 332.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0+$(($padding/2)) 341.png
mogrify -bordercolor transparent -border 0x$(($padding)) -background transparent -extent -0-$(($padding)) 342.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0+$(($padding/2)) 349.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 350.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0+$(($padding/2)) 366.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 367.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0+$(($padding/2)) 376.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 377.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 411.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0+$(($padding/2)) 414.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 415.png
#mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 417.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 418.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 428.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0+$(($padding/2)) 445.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 446.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0+$(($padding/2)) 452.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 453.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 466.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 477.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 483.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 496.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0+$(($padding/2)) 498.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 499.png
mogrify -bordercolor transparent -border 0x$(($padding)) -background transparent -extent -0+$(($padding/2)) 506.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 507.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 511.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 518.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0+$(($padding/2)) 525.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 526.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 542.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0+$(($padding/2)) 548.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 549.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 553.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0+$(($padding/2)) 555.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 556.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0+$(($padding/2)) 557.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 558.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 560.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 562.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 572.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 574.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 582.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0+$(($padding/2)) 584.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 585.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-0 586.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 587.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-0 590.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 591.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 593.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0+$(($padding/2)) 594.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 595.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 597.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 598.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 601.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 602.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 603.png
mogrify -bordercolor transparent -border 0x$(($padding/2)) -background transparent -extent -0-$(($padding/2)) 604.png

echo "Done adjusting padding for PNG files..."
