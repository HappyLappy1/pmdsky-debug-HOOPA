from hoopa_unbound.constants_and_config import CONFIG
from hoopa_unbound.define.symbols_and_headers import SymbolsYamlFile

version = "0.0.1"


if __name__ == '__main__':
    
    
    
    print("\tHOOPA - V%s" % version)
    print(SymbolsYamlFile.from_yaml("/Users/itred/Desktop/Programming/Active_Projects/PMD-FotS-romhack/CoT/pmdsky-debug/symbols/overlay05.yml"))