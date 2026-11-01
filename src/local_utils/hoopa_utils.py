from __future__ import annotations

# Primitive types that Ghidra uses by default aren't always the ones used in the repo
# swap them out with their equivalent 
# Table courtesey of Happylappy
retype_table: dict[str, str] = {
    "ulonglong": "uint64_t",
    "longlong": "int64_t",
    "ushort": "uint16_t",
    "short": "int16_t",
    "byte": "int8_t",
    "code": "undefined*",
    "undefined8": "int64_t"
}


class HoopaUtils:
    
    @staticmethod
    def print_error(contents: str):
        print("\033[95mERROR - %s\033[00m" % contents)
    
    @staticmethod
    def print_info(contents: str):
        print("\033[94mINFO - %s\033[00m" % contents)
        
    @staticmethod
    def print_debug(contents: str):
        print("\033[37mDEBUG - %s\033[00m" % contents)
        
        
    @staticmethod
    def int_to_hex_str_formatted(input: int) -> str:
        """
        Returns the hex-representation of the given integer, in the format used by pmdsky_debug (all alphabetic characters capitalized)
        """
        hex_val = hex(input).upper().replace("X", "x") # Capitalize everything but the "x" in 0x<value>
        # Remove leading zero from value if present
        if hex_val[2] == "0":
            hex_val = "0x" + hex_val.removeprefix("0x0") # I'm really tired and this is the best way I could think of lol
        return hex_val
    
    @staticmethod
    def is_str_hex(input: str) -> bool:
        return True if (input.removeprefix("0x") != input and input.removeprefix("0x").isalnum()) else False
    
    
    @staticmethod
    def to_upper_camel_case(input: str) -> str:
       
        # Capitalize the first letter after any whitespace or underscore
        input_reconstructed = ""
        for i in range(len(input)):
            character = input[i]
            new_character = character
            if i == 0:
                new_character = new_character.upper()
            else:
                new_character = new_character.lower()
            
            if i > 0:
                last_character = input[i - 1]
                if last_character == ' ' or last_character == '_':
                    new_character = new_character.upper()
                    
            
            
            input_reconstructed += new_character
           
           
        input_reconstructed = input_reconstructed \
            .replace(" ", "") \
            .replace("_", "")
        return input_reconstructed
    
    @staticmethod
    def to_screaming_snake_case(input: str) -> str:
        input_reconstructed = ""
        for i in range(len(input)):
            character = input[i]
            
            
            # if this is an alphabetic, uppercase-character that is not the first in the string and not preceded by whitespace (which we deal with later), prepend an underscore to it
            # if this is a numeric character that is not the first in the string, and is preceeded by an alphabetic character, also prepend an underscore to it
            if (i > 0 and character.isalpha() and not character.islower() and not input[i - 1] == ' ') or (i > 0 and character.isnumeric() and input[i - 1].isalpha()): 
                input_reconstructed += "_"
                
                
            character = character.upper()
            input_reconstructed += character
            
        input_reconstructed = input_reconstructed.replace(" ", "_") 
        return input_reconstructed
        
    
    @staticmethod 
    def ghidra_primitive_to_conventional(input_str: str) -> str:
        '''
        Takes a primitive type exported from Ghidra, and converts it to its more conventional equivalent used in the repo
        
        i.e., ushort -> uint16_t, byte -> int8_t, etc.
        
        Returns the same string used as input if the given input string has no equivalent, or is not a type
        '''
        return retype_table[input_str] if input_str in retype_table else input_str
    
    
    @staticmethod
    def indent_string(amount: int = 2, input: str = "") -> str:
        
        indent_complete = ""
        for i in range(amount):
            indent_complete += " "
            
        return indent_complete + input
    
    
    @staticmethod
    def type_to_human_readable(input_string: str) -> str:
        '''
        Really, all this does it turn pointer types from "type*" to "type pointer" for the sake of function argument descriptions
        '''
        if input_string.endswith("*"):
            return input_string[:len(input_string) - 1] + " pointer"
        else:
            return input_string
        
        
    @staticmethod
    def remove_file_extension_from_str(input_string: str) -> str:
        
        index = input_string.find(".")
        if index != -1:
            return input_string[:index]
        else:
            return input_string