from __future__ import annotations
from .hoopa_config import CONFIG_INSTANCE
from os import path, mkdir, scandir
from .local_utils.hoopa_utils import HoopaUtils
from .local_utils.data_types import PMD2OverlayData, PMD2Region, PMD2AddressRange, AddressRange, ROMSectionFileData, ChildROMSection
import yaml
from yaml.parser import Parser

import json


class FileManager:
    
    out_folder: str
    cache_folder: str
    draft_folder: str # TODO
    
    pmdsky_debug_directory: str
    symbols_folder: str
    headers_data_folder: str
    headers_functions_folder: str
    headers_types_folder: str
    
    overlay_sections_data: ROMSections
    
    
    def __init__(self) -> None:
        
        this_directory = path.dirname(path.dirname(__file__))
        HoopaUtils.print_info("Getting interpreter set up, making sure folders can be found...")
        
        self.out_folder = path.join(this_directory, "out")
        if not path.isdir(self.out_folder):
            
            HoopaUtils.print_debug("Remaking output directory at [%s]..." % path.abspath(self.out_folder))
            # I can just remake this one
            mkdir(self.out_folder)
            
        else:
            HoopaUtils.print_debug("Found output directory at [%s]..." % path.abspath(self.out_folder))
            
        self.cache_folder = path.join(this_directory, "cache")
        if not path.isdir(self.cache_folder):
            
            HoopaUtils.print_debug("Remaking cache directory at [%s]..." % path.abspath(self.cache_folder))
            # This too
            mkdir(self.cache_folder)
            
        else:
            HoopaUtils.print_debug("Found cache directory at [%s]..." % path.abspath(self.cache_folder))
        
        self.pmdsky_debug_directory = path.relpath(CONFIG_INSTANCE.repository_path.value, this_directory)
        if not path.isdir(self.pmdsky_debug_directory):
            HoopaUtils.print_error("Path to pmdsky_debug (or a clone of it) was invalid! Check your config.toml!")
            exit(1)
        HoopaUtils.print_debug("Found pmdsky_debug folder at [%s]..." % path.abspath(self.pmdsky_debug_directory))    
            
        self.symbols_folder = path.join(self.pmdsky_debug_directory, "symbols")
        if not path.isdir(self.symbols_folder):
            HoopaUtils.print_error("Somehow could not find symbols folder within your pmdsky_debug folder! Bwuh?????")
            exit(1)
        HoopaUtils.print_debug("Found symbols folder at [%s]..." % self.symbols_folder)
        
        
        self.headers_data_folder = path.join(self.pmdsky_debug_directory, "headers", "data")
        if not path.isdir(self.headers_data_folder):
            HoopaUtils.print_error("Somehow could not find headers/data folder within your pmdsky_debug folder! I'm not sure what to do here????")
            exit(1)
        HoopaUtils.print_debug("Found headers/data folder at [%s]..." % self.headers_data_folder)
        
        
        self.headers_functions_folder = path.join(self.pmdsky_debug_directory, "headers", "functions")
        if not path.isdir(self.headers_functions_folder):
            HoopaUtils.print_error("Somehow could not find headers/functions folder within your pmdsky_debug folder! I'm not sure what to do here????")
            exit(1)
        HoopaUtils.print_debug("Found headers/data folder at [%s]..." % self.headers_functions_folder)
        
        
        self.headers_types_folder = path.join(self.pmdsky_debug_directory, "headers", "types")
        if not path.isdir(self.headers_types_folder):
            HoopaUtils.print_error("Somehow could not find headers/types folder within your pmdsky_debug folder! I'm not sure what to do here????")
            exit(1)
        HoopaUtils.print_debug("Found headers/data folder at [%s]..." % self.headers_types_folder)
        
        self._build_section_tree()    
    
    
    def _build_section_tree(self): 
        
        self.overlay_sections_data = ROMSections()
        
        # Iterate through symbols first
        for symbol_file in scandir(self.symbols_folder):
            
            if symbol_file.is_file() and symbol_file.name.endswith(".yml"):
                
                file_name = HoopaUtils.remove_file_extension_from_str(symbol_file.name)
                
                # This is why all of the fields in ROMSections are pre-defined with no arguments, and also named identically to their file counterparts
                # it allows us to effectively reverse-search to see if the given file is an overlay data file
                # the same is true for the headers
                indv_overlay_data: ROMSectionFileData | None = getattr(self.overlay_sections_data, file_name, None)
                if indv_overlay_data != None:
                    
                    indv_overlay_data.name = file_name
                    indv_overlay_data.yaml_path = symbol_file.path
                    symbol_data = self.get_symbol_data_from_file(symbol_file.path)
                    indv_overlay_data.address_range = symbol_data.range
                    
            if symbol_file.is_dir():
                
                # the handful of child ROM-sections are in folders with the exact same name as their parent
                parent_overlay_data: ROMSectionFileData | None = getattr(self.overlay_sections_data, symbol_file.name, None)
                if parent_overlay_data != None:
                    
                    for sub_file in scandir(symbol_file.path):
                        if sub_file.is_file() and sub_file.name.endswith(".yml"):
                            
                            file_name = HoopaUtils.remove_file_extension_from_str(sub_file.name)
                            child_overlay_data: ChildROMSection | None = getattr(self.overlay_sections_data, file_name, None)
                            
                            if child_overlay_data != None:
                                
                                child_overlay_data.name = file_name
                                child_overlay_data.yaml_path = sub_file.path
                                symbol_data = self.get_symbol_data_from_file(sub_file.path)
                                child_overlay_data.address_range = symbol_data.range
                                
                                # Storing a reference to the child in the parent and a reference to the parent in the child makes things very convenient later
                                parent_overlay_data.children.append(child_overlay_data)
                                child_overlay_data.parent = parent_overlay_data

        for data_header in scandir(self.headers_data_folder):
            
            # No need to check if it's the right file type here, theres nothing else in this folder by definition
            if data_header.is_file():
                
                file_name = HoopaUtils.remove_file_extension_from_str(data_header.name)
                indv_overlay_data: ROMSectionFileData | None = getattr(self.overlay_sections_data, file_name, None)
                if indv_overlay_data != None:
                    
                    indv_overlay_data.header_data_path = data_header.path
                    
            if data_header.is_dir():
                for sub_header in scandir(data_header.path):
                    
                    file_name = HoopaUtils.remove_file_extension_from_str(sub_header.name)
                    indv_overlay_data: ROMSectionFileData | None = getattr(self.overlay_sections_data, file_name, None)
                    if indv_overlay_data != None:
                        
                        indv_overlay_data.header_data_path = data_header.path
        
        for function_header in scandir(self.headers_functions_folder):
                    
            # No need to check if it's the right file type here, theres nothing else in this folder by definition
            if function_header.is_file():
                
                file_name = HoopaUtils.remove_file_extension_from_str(function_header.name)
                indv_overlay_data: ROMSectionFileData | None = getattr(self.overlay_sections_data, file_name, None)
                if indv_overlay_data != None:
                    
                    indv_overlay_data.header_function_path = function_header.path
                    
            if function_header.is_dir():
                for sub_header in scandir(function_header.path):
                    
                    file_name = HoopaUtils.remove_file_extension_from_str(sub_header.name)
                    indv_overlay_data: ROMSectionFileData | None = getattr(self.overlay_sections_data, file_name, None)
                    if indv_overlay_data != None:
                        
                        indv_overlay_data.header_function_path = function_header.path
                
                
        
    
    def get_symbol_data_from_file(self, file_path: str) -> PMD2OverlayData:
        '''
        Opens a given symbol.yml file and collects only the data regarding the overlay the file is declared for
        
        I diiiiidn't quite see a purpose in loading the entirety of every symbol file into RAM as objects
        '''
        
        with open(file_path, "r") as contents:
                            
            symbol_info = ""
            for line in contents:
                if line.strip().startswith("functions"): 
                    contents.close()
                    break
                symbol_info += line 
                
            print(file_path)
            return PMD2OverlayData.from_yaml(symbol_info)
        
    

    
class ROMSections:
    arm9 = ROMSectionFileData()
    arm7 = ROMSectionFileData()
    ram = ROMSectionFileData()
    literals = ROMSectionFileData()
    
    libs = ChildROMSection()
    itcm = ChildROMSection()
    move_effects = ChildROMSection()
    
    overlay00 = ROMSectionFileData()
    overlay01 = ROMSectionFileData()
    overlay02 = ROMSectionFileData()
    overlay03 = ROMSectionFileData()
    overlay04 = ROMSectionFileData()
    overlay05 = ROMSectionFileData()
    overlay06 = ROMSectionFileData()
    overlay07 = ROMSectionFileData()
    overlay08 = ROMSectionFileData()
    overlay09 = ROMSectionFileData()
    overlay10 = ROMSectionFileData()
    overlay11 = ROMSectionFileData()
    overlay12 = ROMSectionFileData()
    overlay13 = ROMSectionFileData()
    overlay14 = ROMSectionFileData()
    overlay15 = ROMSectionFileData()
    overlay16 = ROMSectionFileData()
    overlay17 = ROMSectionFileData()
    overlay18 = ROMSectionFileData()
    overlay19 = ROMSectionFileData()
    overlay20 = ROMSectionFileData()
    overlay21 = ROMSectionFileData()
    overlay22 = ROMSectionFileData()
    overlay23 = ROMSectionFileData()
    overlay24 = ROMSectionFileData()
    overlay25 = ROMSectionFileData()
    overlay26 = ROMSectionFileData()
    overlay27 = ROMSectionFileData()
    overlay28 = ROMSectionFileData()
    overlay29 = ROMSectionFileData()
    overlay30 = ROMSectionFileData()
    overlay31 = ROMSectionFileData()
    overlay32 = ROMSectionFileData()
    overlay33 = ROMSectionFileData()
    overlay34 = ROMSectionFileData()
    overlay35 = ROMSectionFileData()
    
    
FILE_MANAGER = FileManager() # type: ignore
