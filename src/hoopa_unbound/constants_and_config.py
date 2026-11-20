from __future__ import annotations

from typing import Any, Generic, TypeVar, cast
from dataclasses import dataclass, asdict, fields, astuple, field
from os import path

import toml

from hoopa_unbound.define.utility import Pair, SupportsKV, print_error
from hoopa_unbound.define.config import BaseConfigHolder, OneofConfigHolder


# File is currently in `./src/hoopa_unbound/config/config_manager.py`




@dataclass
class _Constants(SupportsKV):
    '''
    Holds constant values used by the program. 
    '''
    # No waaaay really??? I had no idea
    
    source_directory: str = path.dirname(path.dirname(__file__))
    project_directory: str = path.dirname(source_directory)
    
    config_file: str = path.join(project_directory, "config.toml")
    
    config_newline_sep_count: int = 1
        
    def __init__(self) -> None:
        # Found the error the last version of this was giving me to be super annoying and somewhat destructive, so this is my solution
        # the whole module will refuse to run if this isn't in the right spot, and everything else finds relative directories and whatnot from here
        if path.basename(self.source_directory) != "src":
            raise FileNotFoundError("constants_and_config.py was moved!! This error was raised to avoid files and directories from being erroneously written. If you see this, please manually adjust constants_and_config.py!")
    


CONSTANTS = _Constants()


@dataclass
class _Config(SupportsKV):
    '''
    Holds configured values given by the user of the program, from the config.toml file.
    '''
    
    repository_path: BaseConfigHolder[str]
    game_region: OneofConfigHolder[str]
    
    def __init__(self) -> None:
        
        # ! ATTENTION
        # Due to absolute nonsense beyond my comprehension, putting complex objects in a dataclass wont work as intended unless the fields holding those objects are manually assigned in the initializer here
        # if you don't do this, `instance.__dict__` will return nothing, and anything extending off of that (including all of the funky dataclass functionality) will treat those objects as absent
        # I spent aaaggeeess fiddling around with this to try and find why it wasnt working, and this was the only thing that fixed it???
        # not as pretty as it could be but like... what can ya do
        
        self.repository_path = BaseConfigHolder[str](
            "REPOSITORY_PATH", [
                "The location of your clone of pmdsky-debug (or a fork of it).",
                "Should be an absolute path.",
                "",
                "The program expects *its* specific layout of symbol and header files to know where-and-how to paste new information",
                "it will read from this location, but for the sake of security, will never attempt to write to any file there."
            ]
        )
        
        self.game_region = OneofConfigHolder[str](
            "GAME_REGION", [
                "The region of your ROM. Changes which field is used for saving \"address\" and \"length\" by default.",
            ],
            ["NA", "EU", "JP"]
        )
    
        
        if not path.isfile(CONSTANTS.config_file):
            print_error("Configuration file `config.toml` absent! Proceeding as if this is the first run...")
            self.__remake_config()
            print_error(f"A new one has been made at {CONSTANTS.config_file}. Please fill it out before running the program again.")
            exit(1)
        
        else:
            self.__read_config()
    
    
    
    def __remake_config(self):
        
        lines: list[str] = []
        
        for _, config_option in self:
            
            # Performs a cast for us while also making it type-safe
            if isinstance(config_option, BaseConfigHolder):
                lines.extend(config_option.to_lines())
                    
                for _ in range(CONSTANTS.config_newline_sep_count):
                    lines.append("")
        
        with open(CONSTANTS.config_file, "w") as opened_file:
            opened_file.writelines([f"{line}\n" for line in lines]) # Append line seperator
            
            
    def __read_config(self):
        
        data = toml.load(CONSTANTS.config_file)
        any_missing = False
        
        for property_name, property_value in self:
            
            if isinstance(property_value, BaseConfigHolder):
                
                if property_value.name in data:
                    property_value.value = data[property_value.name]
                    # The set will fail if the value is somehow invalid
                    if property_value.value != data[property_value.name]:
                        any_missing = True
                    
                else:
                    any_missing = True
                    
        if any_missing:
            print_error("Some configuration options were missing or invalid! Repairing config.toml...")
            self.__remake_config()
            print_error(f"{CONSTANTS.config_file} has been repaired, and all valid config has been kept. Please fill out the missing values before proceeding.")
            exit(1)
                
        
        
            
        

CONFIG = _Config()
