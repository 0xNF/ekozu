Ekozu
=====

Ekozu is a tool for attempting to identify songs and their start positions within a video or series of videos, if the set of songs inside the videos are known.


## Setup
Ekozu requires Spotify's [EchoPrintCodegen](https://github.com/spotify/echoprint-codegen) and [EchoPrintServer](https://github.com/spotify/echoprint-server) to be installed and available on the system path.
Ekozu also requires [ffmpeg](https://trac.ffmpeg.org/wiki/CompilationGuide) to be installed with audio codec support, and available on the system path. Ffmpeg should be already be available by installing EchoPrint.

Once both of those are installed, you can install Ekozu by running `python setup.py install`

## Usage
### `ekozu` ###

This is the top most level command. Unless you need finer grained control, such as adding an additional song index, this is the only command necessary.

`ekozu.py [-h] [-p] SeriesName videos songs`

`-h` is the help flag, displaying proper usage.

`-p` is the persistent flag, which keeps all generated output, with the more useful information like intermediate song indexes and generated echoprint items located under `/[SeriesName]/tracepaths/`

`SeriesName` is the name of the series, as specified by the user.

`videos` is the path to the videos that you want to analyze

`songs` is the path to the songs that are included in the universe of known songs. `songs` should contain one folder for each source. i.e, if a series has two music CDs, `songs` should contain two folders, one for each CD. You may group all songs together, in which case they should all reside under a single folder underneath `songs`. The name of any of these sub-folders is not important.

The result of the script will be one text file per video showing the start time of a song, and the song name. These files will be located under `/[SeriesName]/episodes/timings.txt`

### `makePrints` ###

### `collectAverages` ###