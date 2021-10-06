#!/usr/bin/env python3
# Author: Markus Bassermann
# 05/10/2021
# Compression method adapted from https://github.com/theeko74/pdfc/blob/master/pdf_compressor.py

import argparse
from typing import List
import sys
import subprocess
from pathlib import Path
import os
import datetime
import shutil

#! TODO
# comprehensive logging-file
# test OS-agnosticism
# Option to ignore high compression level but allow lower level for specific files?

# Constants
ZOTERO_PATH = "D:/Zotero" # Path to Zotero-main-directory
GS_BIN_PATH = "C:/Program Files/gs/gs9.55.0/bin" # only required if ghostscript is not accessible globally (Windows PATH etc.)
STORAGE_DIR = "storage" # Name of directory containing stored files. Should always be "storage" but can be changed for testing purposes

POWER_DEFAULT = 2 # Default for the -p argument
MAX_DEFAULT = 5000 # Default for the -max argument

def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-p', '--power', type=int, help='Compression level from 0 to 4.')
    parser.add_argument('-nb', '--nobackup', action='store_true', help="Don't backup the old PDF file.")
    parser.add_argument('-d', '--dryrun', action='store_true', help="Do a dry-run without any file changes.")
    parser.add_argument('-max', '--max', type=int, help="Max filesize of a pdf in Kilobyte.")
    args = parser.parse_args()

    if args.power is None:
        args.power = POWER_DEFAULT

    if args.max is None:
        args.max = MAX_DEFAULT
    
    path = Path(ZOTERO_PATH, STORAGE_DIR)
    if path.exists() == False:
        raise FileNotFoundError(f"Zotero storage not found at {path}")

    gs_path = get_ghostscript_path()

    print(f'Looking for files at {path}.')

    pdfs : List(Path) = []

    # go through each directory, checking if it contains 1+ pdfs or relevant ignore-markers
    # create a list of pdfs with filesize => args.max
    for child in path.iterdir():
        if not len([file for file in child.iterdir() if check_ignore_conditions(file.name, args.power)]) > 0:
            found_pdfs = [file for file in child.iterdir() if file.name.split('.')[-1].lower() == 'pdf' and file.stat().st_size / 1000 >= args.max]
            pdfs.extend(found_pdfs)

    print(f'Found {len(pdfs)} PDFs to compress')
    
    backup_path = Path(ZOTERO_PATH,'compression_backups',datetime.datetime.now().strftime('%d-%w-%y-%f'))
    if not args.nobackup:
        if not Path(ZOTERO_PATH,'compression_backups').exists():
            Path.mkdir(Path(ZOTERO_PATH,'compression_backups'))
        if not backup_path.exists():
            Path.mkdir(backup_path)

    total_reduction = 0
    for i, pdf in enumerate(pdfs):
        new_path = Path('temp.pdf') #No need to change, it will be deleted/overwritten after the fact
        print(f'Compressing pdf #{i}/{len(pdfs)}: ({str(pdf)}) with original size {pdf.stat().st_size / 1000 / 1000} MB.')

        if not args.dryrun:
            compress(str(pdf),new_path, gs_path, args.power)

            if (new_path.stat().st_size > pdf.stat().st_size):
                print("WARNING: New file size is larger or very close to old file size. Aborting compression...")
            else:
                if not args.nobackup:
                    final_path = Path(backup_path,str(pdf.parents[0]).split('\\')[-1]) #! needs testing if it's OS-agnostic
                    print(f'Writing backup to {final_path}')
                    if not (final_path).exists():
                        Path.mkdir(final_path)
                    shutil.copyfile(str(pdf), Path(final_path,pdf.name))
                total_reduction += (pdf.stat().st_size - new_path.stat().st_size) 
                shutil.copyfile(new_path, str(pdf))

                # create the ignore file after a successful compression
                with Path(pdf.parents[0],f'.zbc.p{args.power}-compressed').open('w', encoding="utf-8") as file:
                    file.write(f"Compressed at: {datetime.datetime.now().strftime('%d-%w-%y-%H-%M-%f')}.")

                print(f"Finished compressing {str(pdf)} for a total reduction of {total_reduction / 1000000} MB so far")
            os.remove(new_path) # The temporary pdf is deleted either way; no need for the new pdf if it's siasdze is larger
        
    print(f"Finished parsing {len(pdfs)} PDFs for a total reduction of {total_reduction / 1000000} MB")

# directly taken from original at https://github.com/theeko74/pdfc/blob/master/pdf_compressor.py
def compress(input_file_path, output_file_path, gs_path, power):
    """Function to compress PDF via Ghostscript command line interface"""
    quality = {
        0: '/default',
        1: '/prepress',
        2: '/printer',
        3: '/ebook',
        4: '/screen'
    }

    # Check if valid path
    if not os.path.isfile(input_file_path):
        print("Error: invalid path for input PDF file")
        sys.exit(1)

    # Check if file is a PDF by extension
    if input_file_path.split('.')[-1].lower() != 'pdf':
        print("Error: input file is not a PDF")
        sys.exit(1)

    print(f"Compress PDF with power {power}...")
    initial_size = os.path.getsize(input_file_path)
    subprocess.call([gs_path, '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                    '-dPDFSETTINGS={}'.format(quality[power]),
                    '-dNOPAUSE', '-dQUIET', '-dBATCH',
                    '-sOutputFile={}'.format(output_file_path),
                     input_file_path]
    )
    final_size = os.path.getsize(output_file_path)
    ratio = 1 - (final_size / initial_size)
    print("Compression by {0:.0%}.".format(ratio))
    print("Final file size is {0:.1f}MB".format(final_size / 1000000))
    print("Done.")

# Implemented pull request & comment https://github.com/theeko74/pdfc/pull/4
def get_ghostscript_path():
    gs_names = ['gs', 'gswin32', 'gswin64']
    for name in gs_names:
        if shutil.which(name):
            return shutil.which(name)
        elif Path(GS_BIN_PATH, f'{name}.exe').exists():
            return shutil.which(str(Path(GS_BIN_PATH, f'{name}.exe')))
    raise FileNotFoundError(f'No GhostScript executable was found on path ({"/".join(gs_names)} or in {GS_BIN_PATH})')

def check_ignore_conditions(filename, power):
    if ('.zbc.' in filename):
        if (filename == '.zbc.ignore'):
            return True
        else:
            for power in range(power,4+1): # check for all higher level compressions as well
                if (filename == f'.zbc.p{power}-compressed'):
                    return True
    return False
    
if __name__ == '__main__':
    main()