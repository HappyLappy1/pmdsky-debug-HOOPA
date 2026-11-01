from data_types import PMD2RegionalData, FunctionArgument, ROMSections
from io import TextIOWrapper, SEEK_END
import os
from enum import StrEnum
from local_utils.hoopa_utils import HoopaUtils




class DocType(StrEnum):
    FUNCTION = "function"
    DATA = "data"

class BaseYamlDocumentObject:
    
    name: str
    address: PMD2RegionalData
    length: PMD2RegionalData
    description: list[str]
    target_overlay: ROMSections
    
    def get_full_yaml_string(self, indent: int = 0) -> str:
        
        final_string = "\n"
        
        # Always goes name, then address, then length, THEN description
        indent_str = HoopaUtils.indent_string(indent)
    
        final_string += "%s- name: %s\n" % (indent_str, self.name)
        
        if getattr(self, "address"):
            final_string += self._get_address_string(indent + 2)
        
        if getattr(self, "length"):
            final_string += self._get_length_string(indent + 2)
            
        if getattr(self, "description"):
            final_string += self._get_desc_string(indent + 2)
        
        return final_string
        
    
    # In its own function to make overriding easier
    def _get_desc_string(self, indent: int = 0) -> str:
        
        indent_str = HoopaUtils.indent_string(indent)
        output_string = "%sdescription:" % indent_str
        
        if len(self.description) == 0:
            output_string += ' "%s"' % self.description
        else:
            output_string += " |-\n"
            
            indent_str += "  "
            for line in self.description:
                output_string += "%s%s\n" % (indent_str, line)
        
        return output_string
                
    
    def _get_address_string(self, indent: int = 0) -> str:
        
        indent_str = HoopaUtils.indent_string(indent)
        output_string = "%slength:\n" % indent_str
        indent_str += "  " # 2 indent from address block
        
        for region in ["EU", "NA", "JP"]:
            data = getattr(self.length, region)
            if data:
                output_string += "%s%s: %s\n" % (indent_str, region, data)
                
        return output_string
                
        
    def _get_length_string(self, indent: int = 0):
        
        indent_str = HoopaUtils.indent_string(indent)
        output_string = "%saddress:\n" % indent_str
        indent_str += "  " # 2 indent from address block
        
        for region in ["EU", "NA", "JP"]:
            data = getattr(self.address, region)
            if data:
                output_string += "%s%s: %s\n" % (indent_str, region, data)
        
        return output_string
                    
    
    

class DataYamlDocumentObject(BaseYamlDocumentObject): 
    
    type: str
    include_type_in_description: bool = True # true by default, I find Ghidra is inconsistent about making them stick when importing
    
    
    def _get_desc_string(self, indent: int = 0) -> str:
        
        indent_str = HoopaUtils.indent_string(indent)
        output_string = "%sdescription:" % indent_str
        
        # We use a multi-line description if we're including the type in the description, regardless of whether the description has multiple lines or not
        if len(self.description) == 0 and not self.include_type_in_description:
            output_string += ' "%s"' % self.description
        else:
            output_string += " |-\n"
            
            indent_str += "  "
            for line in self.description:
                output_string += "%s%s\n" % (indent_str, line)
                
            if self.include_type_in_description:
                output_string += "\n\n%s" % self.type
        
        return output_string
    
    

class FunctionYamlDocumentObject(BaseYamlDocumentObject):
    
    return_type: str
    arguments: list[FunctionArgument]
    include_types_in_description: bool = True # true by default, same thing as with the Data one
    
    def _get_desc_string(self, indent: int = 0) -> str:
            
        indent_str = HoopaUtils.indent_string(indent)
        output_string = "%sdescription:" % indent_str
        
        # We use a multi-line description if we're including the types in the description, regardless of whether the description has multiple lines or not
        if len(self.description) == 0 and not self.include_types_in_description:
            output_string += ' "%s"' % self.description
        else:
            output_string += " |-\n"
            
            indent_str += "  "
            for line in self.description:
                output_string += "%s%s\n" % (indent_str, line)
                
            if self.include_types_in_description:
                output_string += "\n\n"
                
                if getattr(self, "arguments"):
                    index = 0
                    for arg in self.arguments:
                        output_string += "%sr%s: %s\n" % (indent_str, index, HoopaUtils.type_to_human_readable(arg.type))

                if getattr(self, "return_type"):
                    output_string += "%sreturns: %s\n" % (indent_str, HoopaUtils.type_to_human_readable(self.return_type))
        
        return output_string
    
        
        
        
    
root_project_dir = os.path.dirname(
    os.path.dirname( os.path.dirname(__file__) )
)
        
dat = BaseYamlDocumentObject()
dat.name = "TestSymbol"
dat.address = PMD2RegionalData(0x6300000, 0x4000000)
dat.length = PMD2RegionalData(0x4, 0x6)
dat.description = ["This description spans across multiple lines.", "", "Wow!"]

with open(os.path.join(root_project_dir, "out/test.yml"), "w") as out:
    out.write(dat.get_full_yaml_string())
        
        
        
    