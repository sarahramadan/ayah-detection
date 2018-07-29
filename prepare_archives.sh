#!/bin/bash
set -e

if [ "$#" -ne 6 ]; then
  echo "Usage: $0 <IMAGE_PADDING> <SVG_INPUT_FOLDER> <SQL_INPUT_FOLDER> <IMAGES_OUTPUT_FOLDER> <ARCHIVES_OUTPUT_FOLDER> <RECITATION_ID>" >&2
  exit 1
fi

if [ "$ENCRYPTION_KEY" == "" ]; then
  echo "Must set ENCRYPTION_KEY environment variable"
  exit 1
fi

if [ "$ENCRYPTION_IV" == "" ]; then
  echo "Must set ENCRYPTION_IV environment variable"
  exit 1
fi

padding=$1
svg_input_folder=$2
sql_input_folder=$3
images_output_folder_base=$4
archives_output_folder=$5
recitation_id=$6

# set bash verbose mode
set -x

for width in 320 480 800 1200 1500; do
  archive_root=`mktemp -d`
  archive_name=`echo -n ${recitation_id}_${width}.zip | md5sum | cut -d' ' -f1`
  # generate PNGs for sizes othen than the reference 800
  if [ "$width" != "800" ]; then
    ./svg2png.sh $width $padding $svg_input_folder $images_output_folder_base
  fi
  # reduce color palette to 256 for all sizes
  mogrify -colors 256 -depth 8 +dither $images_output_folder_base/$width/*.png
  # encrypt images
  (
    cd $images_output_folder_base/$width
    find -name "*.png" -exec \
      openssl enc -aes-128-cbc \
      -in {} \
      -out $archive_root/{} \
      -K $ENCRYPTION_KEY \
      -iv $ENCRYPTION_IV \
      \;
  )
  # create archive
  mkdir -p $archives_output_folder
  cp $sql_input_folder/$width.sql $archive_root/data.txt
  # -n to skip compression for suffix .png (no need, don't even try and waste time)
  # -m to delete after zipping
  # -j to exclude path names
  zip -n .png -m -j -q $archives_output_folder/$archive_name.zip $archive_root/*
  # .zip extension is added automatically even if not specified, remove it
  mv $archives_output_folder/$archive_name.zip $archives_output_folder/$archive_name
done
