# Zotero Bulk PDF Compression

A commandline tool to compress all PDFs in Zotero's "storage"-directory, using ghostscript. Adapted theeko74's [single-file compression script](https://github.com/theeko74/pdfc).

## Setup & Requirements

 * Make sure [Ghostscript](https://www.ghostscript.com/) is installed
* Open the .py file and update ZOTERO_PATH to reflect the location of Zotero's main folder. E.g. `"C:/Program Files/Zotero"` for Windows.
*  Make sure Ghostscript is accessible through commandline (e.g. by configuring Windows' PATH-variable)
   * **Alternatively**: If Ghostscript is not accessible through commandline make sure GS_BIN_PATH points to the bin-directory of the installed release. E.g. `"C:/Program Files/gs/gs9.55.0/bin"` for Windows.
* Optional: For testing purposes, you can modify STORAGE_DIR to the name of a different directory, *within the main Zotero-directory*.


## Usage

Run `zoterobulkcompression.py` as python-script through terminal. By default, backups will be created for each file in the Zotero main-directory.

Available arguments (all optional):

`zoterobulkcompression [-p <number>] [-nb] [-d] [-max <number>]`

### Options:
* -p[ower]: compression level from 0(lowest) to 4(highest) | default: 2
* -n[o]b[ackup]: Script will **not** create a backup for each pdf
* -d[ryrun]: Script will only list all pdfs it found, without any actual compression
* -max: all files with a kb-size > max will be compressed | default: 5000

## Ignoring files
* To ignore a specific PDF add a file named `.zbc.ignore` to it's directory.
* To ignore specific compression levels for a pdf, add `.zbc.p0-compressed` to it's directory, with 0 being any number from 0 to 4. This compression level and any lower level won't be applied. **Note** ZBC also adds this file automatically after a successful run.

## Credits/Thanks
* Sylvain Carlioz for [pdfc](https://github.com/theeko74/pdfc).
* skjerns & runcioa for [their pull request and comments](https://github.com/theeko74/pdfc/pull/4)
