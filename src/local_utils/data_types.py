from __future__ import annotations
from local_utils.hoopa_utils import HoopaUtils
from enum import Enum, StrEnum
from typing import Any
import yaml
from io import TextIOWrapper, SEEK_END


class PMD2Region(StrEnum):
    REGION_EU = "EU"
    REGION_NA = "NA"
    REGION_JP = "JP"
    
    
class PMD2RegionalData:
    EU: str
    NA: str
    JP: str
    
    def __init__(self, valueNA = -1, valueEU = -1, valueJP = -1) -> None:
        self.EU = HoopaUtils.int_to_hex_str_formatted(valueEU) if valueEU > -1 else ""
        self.NA = HoopaUtils.int_to_hex_str_formatted(valueNA) if valueNA > -1 else ""
        self.JP = HoopaUtils.int_to_hex_str_formatted(valueJP) if valueJP > -1 else ""
    
    @staticmethod
    def from_dict(data: dict) -> PMD2RegionalData:
        return PMD2RegionalData(
            data["NA"] if "NA" in data else -1,
            data["EU"] if "EU" in data else -1,
            data["JP"] if "JP" in data else -1,
        )
    
        
    def is_empty(self):
        """
        Returns whether this regional docstring has any of its fields filled out.
        """
        return True if self.NA == "" and self.EU == "" and self.JP == "" else False

    ### Thought this would be needed, but seemingly vars(object) keeps order based on declaration within the object itself?? Possibly???
    ### It SEEMS consistent, and shifting the declaration in the __init__ function shifts the order in the dictionary given by vars(object)
    ### So????? OKay??
    def get_ordered_values(self):
        return {
            "EU": self.EU,
            "NA": self.NA,
            "JP": self.JP
        }        


class AddressRange:
    addr_from: int
    addr_to: int
    addr_len: int
    
    def __init__(self, addr_from, addr_to) -> None:
        self.addr_from = addr_from
        self.addr_to = addr_to
        self.addr_len = addr_to - addr_from
        
    def __str__(self) -> str:
        return "ADDRESSRANGE - From: %s, To: %s, Length: %s" % (
            HoopaUtils.int_to_hex_str_formatted(self.addr_from), HoopaUtils.int_to_hex_str_formatted(self.addr_to), HoopaUtils.int_to_hex_str_formatted(self.addr_len)
            )
    
    def get_json(self) -> dict[str, int]:
        return {"from": self.addr_from, "to": self.addr_to, "length": self.addr_len}
    


class PMD2AddressRange:
    EU: AddressRange
    NA: AddressRange
    JP: AddressRange
    
    def __init__(self, NA: list[int] = [], EU: list[int] = [], JP: list[int] = []) -> None:
        if len(NA) == 2:
            self.NA = AddressRange(NA[0], NA[1])
        if len(EU) == 2:
            self.EU = AddressRange(EU[0], EU[1])
        if len(JP) == 2:
            self.JP = AddressRange(JP[0], JP[1])
            
            
    def get_json(self) -> dict[str, dict[str, int]]:
        data = {}
        if getattr(self, "NA"):
            data["NA"] = self.NA.get_json()
        if getattr(self, "EU"):
            data["EU"] = self.EU.get_json()
        if getattr(self, "JP"):
            data["JP"] = self.JP.get_json()
        return data
        
   
class FunctionArgument:
    label: str
    type: str
    

# "I used the Python to write the Python"
# - itred, 2026
class ROMSections:
    ARM9 = PMD2AddressRange( NA=[0x2000000, 0x20B73F8], EU=[0x2000000, 0x20B7D38], JP=[0x2000000, 0x20B8CB8] )
    ARM7 = PMD2AddressRange( NA=[0x2380000, 0x23A7080], EU=[0x2380000, 0x23A7080], JP=[0x2380000, 0x23A7080] )
    RAM = PMD2AddressRange( NA=[0x2000000, 0x2400000], EU=[0x2000000, 0x2400000], JP=[0x2000000, 0x2400000] )
    LITERALS = PMD2AddressRange( NA=[0x2000000, 0x20B73F8], EU=[0x2000000, 0x20B7D38], JP=[0x2000000, 0x20B8CB8] )
    LIBS = PMD2AddressRange( NA=[0x206C0D8, 0x20908D4], EU=[0x206C470, 0x2090C6C], JP=[0x206C3C0, 0x2090BBC] )
    ITCM = PMD2AddressRange( NA=[0x20B3380, 0x20B7380], EU=[0x20B3CC0, 0x20B7CC0], JP=[0x20B4BE0, 0x20B8C40] )
    MOVE_EFFECTS = PMD2AddressRange( NA=[0x2325DC0, 0x232E80C], EU=[0x2326828, 0x232F24C], JP=[0x232724C, 0x232FC08] )
    
    OVERLAY_00 = PMD2AddressRange( NA=[0x22BCA80, 0x231D420], EU=[0x22BD3C0, 0x231DC40], JP=[0x22BE220, 0x231EBC0] )
    OVERLAY_01 = PMD2AddressRange( NA=[0x2329520, 0x233C240], EU=[0x2329D40, 0x233C9C0], JP=[0x232ACC0, 0x233DAC0] )
    OVERLAY_02 = PMD2AddressRange( NA=[0x2329520, 0x23544C0], EU=[0x2329D40, 0x2354D00], JP=[0x232ACC0, 0x2355C60] )
    OVERLAY_03 = PMD2AddressRange( NA=[0x233CA80, 0x2346BE0], EU=[0x233D200, 0x2347360], JP=[0x233E300, 0x2348460] )
    OVERLAY_04 = PMD2AddressRange( NA=[0x233CA80, 0x233F660], EU=[0x233D200, 0x233FDE0], JP=[0x233E300, 0x2340EE0] )
    OVERLAY_05 = PMD2AddressRange( NA=[0x233CA80, 0x233FCC0], EU=[0x233D200, 0x2340440], JP=[0x233E300, 0x2341560] )
    OVERLAY_06 = PMD2AddressRange( NA=[0x233CA80, 0x233EEE0], EU=[0x233D200, 0x233F660], JP=[0x233E300, 0x2340760] )
    OVERLAY_08 = PMD2AddressRange( NA=[0x233CA80, 0x233EC80], EU=[0x233D200, 0x233F820], JP=[0x233E300, 0x2340500] )
    OVERLAY_07 = PMD2AddressRange( NA=[0x233CA80, 0x2341B80], EU=[0x233D200, 0x2340500], JP=[0x233E300, 0x23436E0] )
    OVERLAY_09 = PMD2AddressRange( NA=[0x233CA80, 0x233F800], EU=[0x233D200, 0x233FF80], JP=[0x233E300, 0x2341020] )
    OVERLAY_10 = PMD2AddressRange( NA=[0x22BCA80, 0x22DC220], EU=[0x22BD3C0, 0x22DCB60], JP=[0x22BE220, 0x22DD8C0] )
    OVERLAY_11 = PMD2AddressRange( NA=[0x22DC240, 0x2324E80], EU=[0x22DCB80, 0x23259C0], JP=[0x22DD8E0, 0x23263E0] )
    OVERLAY_12 = PMD2AddressRange( NA=[0x238A140, 0x238A160], EU=[0x238AC80, 0x238ACA0], JP=[0x238B6A0, 0x238B6C0] )
    OVERLAY_13 = PMD2AddressRange( NA=[0x238A140, 0x238CFC0], EU=[0x238AC80, 0x238DB00], JP=[0x238B6A0, 0x238E520] )
    OVERLAY_14 = PMD2AddressRange( NA=[0x238A140, 0x238DC20], EU=[0x238AC80, 0x238E7C0], JP=[0x238B6A0, 0x238F180] )
    OVERLAY_15 = PMD2AddressRange( NA=[0x238A140, 0x238B1A0], EU=[0x238AC80, 0x238BD00], JP=[0x238B6A0, 0x238C700] )
    OVERLAY_16 = PMD2AddressRange( NA=[0x238A140, 0x238CE60], EU=[0x238AC80, 0x238D9A0], JP=[0x238B6A0, 0x238E3E0] )
    OVERLAY_17 = PMD2AddressRange( NA=[0x238A140, 0x238BE20], EU=[0x238AC80, 0x238C960], JP=[0x238B6A0, 0x238D380] )
    OVERLAY_18 = PMD2AddressRange( NA=[0x238A140, 0x238D640], EU=[0x238AC80, 0x238E180], JP=[0x238B6A0, 0x238EBC0] )
    OVERLAY_19 = PMD2AddressRange( NA=[0x238A140, 0x238E380], EU=[0x238AC80, 0x238EEA0], JP=[0x238B6A0, 0x238F8C0] )
    OVERLAY_20 = PMD2AddressRange( NA=[0x238A140, 0x238D140], EU=[0x238AC80, 0x238DC80], JP=[0x238B6A0, 0x238E6A0] )
    OVERLAY_21 = PMD2AddressRange( NA=[0x238A140, 0x238CF60], EU=[0x238AC80, 0x238DAA0], JP=[0x238B6A0, 0x238E4E0] )
    OVERLAY_22 = PMD2AddressRange( NA=[0x238A140, 0x238EC80], EU=[0x238AC80, 0x238F7C0], JP=[0x238B6A0, 0x23901E0] )
    OVERLAY_23 = PMD2AddressRange( NA=[0x238A140, 0x238D8C0], EU=[0x238AC80, 0x238E400], JP=[0x238B6A0, 0x238EE80] )
    OVERLAY_24 = PMD2AddressRange( NA=[0x238A140, 0x238C620], EU=[0x238AC80, 0x238D160], JP=[0x238B6A0, 0x238DB80] )
    OVERLAY_25 = PMD2AddressRange( NA=[0x238A140, 0x238B600], EU=[0x238AC80, 0x238C140], JP=[0x238B6A0, 0x238CB60] )
    OVERLAY_26 = PMD2AddressRange( NA=[0x238A140, 0x238AF80], EU=[0x238AC80, 0x238BAC0], JP=[0x238B6A0, 0x238C4E0] )
    OVERLAY_27 = PMD2AddressRange( NA=[0x238A140, 0x238CEA0], EU=[0x238AC80, 0x238D9E0], JP=[0x238B6A0, 0x238E440] )
    OVERLAY_28 = PMD2AddressRange( NA=[0x238A140, 0x238ADA0], EU=[0x238AC80, 0x238B8E0], JP=[0x238B6A0, 0x238C300] )
    OVERLAY_29 = PMD2AddressRange( NA=[0x22DC240, 0x2353860], EU=[0x22DCB80, 0x2354480], JP=[0x22DD8E0, 0x2354AE0] )
    OVERLAY_30 = PMD2AddressRange( NA=[0x2382820, 0x23860C0], EU=[0x2383420, 0x2386CC0], JP=[0x2383AA0, 0x2387320] )
    OVERLAY_31 = PMD2AddressRange( NA=[0x2382820, 0x238A2A0], EU=[0x2383420, 0x238AEC0], JP=[0x2383AA0, 0x238B560] )
    OVERLAY_32 = PMD2AddressRange( NA=[0x2382820, 0x2382840], EU=[0x2383420, 0x2383440], JP=[0x2383AA0, 0x2383AC0] )
    OVERLAY_33 = PMD2AddressRange( NA=[0x2382820, 0x2382840], EU=[0x2383420, 0x2383440], JP=[0x2383AA0, 0x2383AC0] )    
    OVERLAY_34 = PMD2AddressRange( NA=[0x22DC240, 0x22DD0A0], EU=[0x22DCB80, 0x22DD940], JP=[0x22DD8E0, 0x22DE6A0] )
    OVERLAY_35 = PMD2AddressRange( NA=[0x22BCA80, 0x22BCAA0], EU=[0x22BD3C0, 0x22BD3E0], JP=[0x22BE220, 0x22BE240] )
    
    
    
    
    
    
   
    
    

    



class PMD2OverlayData:
    name: str
    versions: list[PMD2Region]
    addresses: PMD2RegionalData
    length: PMD2RegionalData
    description: str
    
    range: PMD2AddressRange
    
    
    def __init__(self, name: str, versions: list[PMD2Region], addresses: dict[PMD2Region, int], length: dict[PMD2Region, int], description: str) -> None:
        self.name = name
        self.versions = versions
        self.addresses = PMD2RegionalData.from_dict(addresses)
        self.length = PMD2RegionalData.from_dict(length)
        self.description = description
        
        self.range = PMD2AddressRange(
            [int(self.addresses.NA, 16), int(self.addresses.NA, 16) + int(self.length.NA, 16)],
            [int(self.addresses.EU, 16), int(self.addresses.EU, 16) + int(self.length.EU, 16)],
            [int(self.addresses.JP, 16), int(self.addresses.JP, 16) + int(self.length.JP, 16)]
        )
    
    
    @staticmethod
    def from_yaml(data: str) -> PMD2OverlayData:
        parsed_data: dict[str, Any] = yaml.safe_load(data)
        
        for overlayname, overlay_data in parsed_data.items():
            return PMD2OverlayData(
                overlayname,
                overlay_data["versions"],
                overlay_data["address"],
                overlay_data["length"],
                overlay_data["description"]
            )
            
            
            
