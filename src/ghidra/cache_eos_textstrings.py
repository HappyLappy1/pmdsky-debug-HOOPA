from __future__ import annotations
from ndspy.rom import NintendoDSRom
from skytemple_files.common.types.file_types import FileType
import json
import sys
from os import path


def create_cache(nds_path: str):
    
    rom = NintendoDSRom.fromFile(nds_path)
    # English for now
    raw_strings = rom.getFileByName("MESSAGE/text_e.str")
    text_strings = FileType.STR.deserialize(raw_strings)
    
    dir_path = path.dirname(__file__)
    file_path = path.join(dir_path, "ghidra_scripts", "text_strings.json")
    
    with open(file_path, "w") as output:
        json.dump(text_strings.strings, output, indent=2)
    
    

if __name__ == "__main__":
    
    if len(sys.argv) == 1:
        print("\n\tcache_eos_textstrings\n\n\033[95mError - No path provided. Run this script with a path to an (preferably unmodified) EOS rom to parse as its argument.\033[00m\n")
        exit(1)
    else:
        create_cache(sys.argv[1])