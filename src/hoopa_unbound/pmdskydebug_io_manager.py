from __future__ import annotations
from os import path
from typing import cast

from hoopa_unbound.constants_and_config import CONSTANTS, CONFIG
from hoopa_unbound.define.utility import print_error

class PmdskyDebugIOManager:
    
    
    symbols_folder: str
    headers_data_folder: str
    headers_functions_folder: str
    
    
    def capture_symbols_and_headers(self):
        
        main_folder = CONFIG.repository_path.value
        if main_folder == None:
            raise FileNotFoundError("HOOPA_UNBOUND - ERROR: PMDSky-debug main folder not defined in config! Technically speaking, this message will never appear. But what am I supposed to do if it does?") # Slash reference
        cast(str, main_folder)
        
        if not path.isdir(main_folder):
            raise NotADirectoryError(f"HOOPA_UNBOUND - ERROR: PMDsky-debug folder configured to point to [ {main_folder} ], which is not a directory!")
        
        
        self.symbols_folder = path.join(main_folder, "symbols")
        if not path.isdir(self.symbols_folder):
            raise NotADirectoryError(f"HOOPA_UNBOUND - ERROR: The symbols folder, which points to [ {self.symbols_folder} ], is not a directory! How did this happen??")
        
        self.headers_data_folder = path.join(main_folder, "headers", "data")
        if not path.isdir(self.headers_data_folder):
            raise NotADirectoryError(f"HOOPA_UNBOUND - ERROR: The headers/data folder, which points to [ {self.headers_data_folder} ], is not a directory! How did this happen??")
        
        self.headers_functions_folder = path.join(main_folder, "headers", "functions")
        if not path.isdir(self.headers_functions_folder):
            raise NotADirectoryError(f"HOOPA_UNBOUND - ERROR: The headers/functions folder, which points to [ {self.headers_functions_folder} ], is not a directory! How did this happen??")
        
        