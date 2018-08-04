# ElMohafez Aya Detectors

بسم الله الرحمن الرحيم

## System requirements

Make sure you have [Docker](https://docs.docker.com/install/) installed on your system.
If you are using Docker for Windows, make sure you enable Linux containers.

## Get the latest Docker image

For the first time, or whenever you need to make sure you have the latest image,
you need to pull the docker image that is used to run the below scripts.

    docker pull elmohafez/ayah-detection:latest

## Run the Docker container

In the below scripts, open a bash shell container based on
the image you pulled/built in the previous step, then run all the scripts under this shell.

    docker run -it --rm elmohafez/ayah-detection:latest

This will open a bash shell where you can run all the scripts.
For example:

    ./svg2png.sh ...
    ./detect_lines.py ...

Type `exit` when done to stop the shell container and return to your host shell.

## Steps for new recitations

Locate the SVG folder that contains 604 images in SVG format.
In the below examples, we assume this is located at `~/Downloads/MHFZ_SOSY`.
You must mount this as a volume when launching your Docker container.

    docker run -it --rm -v ~/Downloads/MHFZ_SOSY:/svg elmohafez/ayah-detection:latest

### 1. Convert SVG to PNG

    ./svg2png.sh 800 10 /svg /svg/output/images

Where:
* `800` is the desired image width, known as reference width
* `10` is the padding to add to images
* `/svg` is the input folder (mounted by docker)
* `/svg/output/images` is the output folder to store resulting images

*IMPORTANT*:
Please note that this script modifies SVG files by removing some paths from them.
If you want to preserve them for further editing, it is advised that
you copy them first and work on the new copy.

### 2. Make sure all PNG images are stored in RGBA format

    ./fix_color_mode.py --input_path /svg/output/images/800

Where `--input_path` is the generated folder from the previous step.

### 3. Detect text lines for each page

    ./detect_lines.py \
      --input_path /svg/output/images/800 \
      --output_path /svg/output \
      --start_page 1 \
      --end_page 10

Where:
* `--input_path` is the path to input folder containing PNG images
* `--output_path` is the path to output folder to generate verification images in
* `--start_page` is an optional start page (default is 1)
* `--end_page` is an optional end page (default is 604)

*IMPORTANT*:
Manually verify all the generated images under `--output_path/lines`
to make sure lines are properly separated with no or minor overlap
between text. If necessary, edit the corresponding SVGs to minimize
any overlap.

### 4. Detect verse separators using image templates for each page

    ./detect_ayat.py \
      --input_path /svg/output/images/800 \
      --output_path /svg/output \
      --separator1_path ./separator1.png \
      --separator3_path ./separator3.png \
      --count_method basry \
      --matching_threshold 0.42 \
      --start_page 560 \
      --start_sura 66 \
      --start_aya 1 \
      --end_page 604

Where:
* `--input_path` is the path to input folder containing PNG images
* `--output_path` is the path to output folder to generate verification images in
* `--separator1_path` is the path to separator image template for pages 1 and 2
* `--separator3_path` is the path to separator image template for pages 3 up to the end
* `--count_method` is the counting method to use (choices are `{basry,shamy,madany2,madany1,kofy,makky}`)
* `--matching_threshold` is an optional matching threshold to match aya separators, default = 0.42
* `--start_page` is an optional start page (default is 1)
* `--start_sura` is an optional start sura (default is 1)
* `--start_aya` is an optional start aya (default is 1)
* `--end_page` is an optional end page (default is 604)

If you want to start from the middle, make sure the first sura and aya in that page are
specified correctly in `--start_sura` and `--start_aya`.

*IMPORTANT*:
Manually verify all the generated images under `--output_path/ayat`
to make sure all aya separators are identified correctly.
Based on the detection, aya regions are highlighted in random colors
with a small text overlaid on each region. It is in the format
`aya:region[sura]`. Sura headers have the special aya number `-1`
while basmalah verses have the number `0`.

The script may fail in the middle if any separator is missed causing
aya counts to go beyond array boundaries. In such case, manually
check which page the first misdetection happened at, and restart
the script from there, but with a slightly modified `--matching_threshold`.
For example, a very small missed separator requires a lower threshold.
So you can try `0.39`. Do not restart the script from page 1 so that
you don't get different errors in the early pages.

### 5. Generate encoded region files

After manually verifying lines and aya regions, it is time to generate
region files for each screen resolution in a format that is compatible
with Android, iOS and Windows.

    ./sqlite_encoder.py \
      --input_path /svg/output/segments \
      --output_path /svg/output/encoded \
      --reference_width 800 \
      --recitation_id 4

Where:
* `--input_path` is the path to input folder containing segmented data SQL files to import
* `--output_path` is the path to output folder to generate platform specific files into
* `--reference_width` is the reference width of which segmented data SQL files were generated
  (the same one that you used in step 1)
* `--recitation_id` is the recitation ID of the segmented data
  (check `recitations.csv` for the complete list)

### 6. Generate archives, ready for the cloud

The final step is to generate the archives that will be uploaded to the cloud.
Each archive is a zip file containing encrypted images plus the regions file.
A separate archive is generated for each screen resolution.

    ./prepare_archives.sh \
      10 \
      /svg \
      /svg/output/encoded \
      /svg/output/images \
      /svg/output/archives \
      4

Where:
* `10` is the padding to add to images (same as you used in step 1)
* `/svg` is the input folder (mounted by docker)
* `/svg/output/encoded` is the input folder containing generated region files from the previous step
* `/svg/output/images` is the output folder to store resulting images
* `/svg/output/archives` is the output folder to store resulting archives
* `4` is the recitation ID

*IMPORTANT*:
For this script to run, you must supply 2 environment variables for encryption to work.
These must match the keys used inside the app to decode the images.
They are namely:
* `ENCRYPTION_KEY`: Encryption Key
* `ENCRYPTION_IV`: Initialization Vector

You can pass these 2 from the docker command with the `-e` switch, example:

    docker run -it --rm -e ENCRYPTION_KEY=<KEY> -e ENCRYPTION_IV=<IV> elmohafez/ayah-detection:latest

### 7. Upload archives to the cloud

Just upload the generated archives from the previous step
to the configured cloud server as is.

### 8. Update the mobile apps

#### 8.1 iOS

Four steps are required to support the new recitation:

* Edit `ElMohafez/sources/recitations.csv` to enable the recitation
  and to set its mediaType to 1 (images).
* Add `/svg/output/encoded/RecitationData<ID>.tsv` to the project under
  `ElMohafez/sources/`
* Add a new dictionary to `ElMohafez/sources/Seed.plist` to refer to the newly
  added file under the dictionary `RecitationsData`.
* Increase the app bundle version to trigger a CoreData migration.

#### 8.2 Android

TODO

#### 8.3 Windows

TODO

## Steps for updated recitations

TODO modify scripts to automate this scenario.
Also do image diff and sql diff to identify changes alone.

### First Run:

You simply mount the new SVG folder with the changed pages only
and do all the steps as above with a few exceptions:

1. The generated SQLs in step 5 must contain a delete statement
in the first line to remove the older records in preparation of
adding the modified records. If no regions were changed, just place
an empty file in the archive.

2. The archive name must be appended with `_patch` and must contain
all the updates happened to the original archive. So if there are 3
updates to apply, this archive must contain all the chanaged pages
in all the 3 updates.

3. TODO Put new instructions for mobile platform specific projects

### Second Run:

You also need to copy any changed files from the First Run to
the original run (the whole SVGs) and repeat all the steps to upload
a modified archive.

## License

MIT

## Acknowledgements

This is based on [Quran Utilities](https://github.com/quran/ayah-detection)
from quran organizatoin.
