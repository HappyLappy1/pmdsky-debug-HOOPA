from __future__ import annotations
from enum import StrEnum
from dataclasses import dataclass
from typing import Any

from hoopa_unbound.define.utility import

class Region(StrEnum):
    EU = "EU"
    NA = "NA"
    JP = "JP"
    
# It's a uhhhh regional dialect
@dataclass
class RegionalData:
    '''
    A piece of data defined once for each region of the game. 
    
    May or may not vary for each region.
    
    May or may not be present for each region.
    '''
    EU: int
    NA: int
    JP: int
    
    def __init__(self, EU: int = 0, NA: int = 0, JP: int = 0) -> None:
        self.EU = EU
        self.NA = NA
        self.JP = JP
        
    
        


class SymbolsYamlFile:
    pass


class Symbol:
    name: str
    description: list[str]
    address: