
import java.io.FileWriter;
import java.io.Writer;
import java.util.Iterator;
import com.google.gson.FormattingStyle;
import com.google.gson.stream.JsonWriter;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.address.AddressRangeIterator;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.symbol.SourceType;

public class HoopaExporter extends GhidraScript {

    // TODO: GRAB FUNCTION/SYMBOL DESCRIPTION TOO

    public enum Region {
        EU("EU"),
        NA("NA"),
        JP("JP");
    
        public final String regionString;

        private Region(String regionString) {
            this.regionString = regionString;
        }
    }

    // Oh, Java enums, how I've missed you...
    public enum Overlay {
        ARM9("arm9"),
        ARM7("arm7"),
        RAM("ram"),
        LITERALS("literals"),
        LIBS("libs"),
        ITCM("itcm"),
        MOVE_EFFECTS("move_effects"),

        OVERLAY_00("overlay00"),
        OVERLAY_01("overlay01"),
        OVERLAY_02("overlay02"),
        OVERLAY_03("overlay03"),
        OVERLAY_04("overlay04"),
        OVERLAY_05("overlay05"),
        OVERLAY_06("overlay06"),
        OVERLAY_07("overlay07"),
        OVERLAY_08("overlay08"),
        OVERLAY_09("overlay09"),
        OVERLAY_10("overlay10"),
        OVERLAY_11("overlay11"),
        OVERLAY_12("overlay12"),
        OVERLAY_13("overlay13"),
        OVERLAY_14("overlay14"),
        OVERLAY_15("overlay15"),
        OVERLAY_16("overlay16"),
        OVERLAY_17("overlay17"),
        OVERLAY_18("overlay18"),
        OVERLAY_19("overlay19"),
        OVERLAY_20("overlay20"),
        OVERLAY_21("overlay21"),
        OVERLAY_22("overlay22"),
        OVERLAY_23("overlay23"),
        OVERLAY_24("overlay24"),
        OVERLAY_25("overlay25"),
        OVERLAY_26("overlay26"),
        OVERLAY_27("overlay27"),
        OVERLAY_28("overlay28"),
        OVERLAY_29("overlay29"),
        OVERLAY_30("overlay30"),
        OVERLAY_31("overlay31"),
        OVERLAY_32("overlay32"),
        OVERLAY_33("overlay33"),
        OVERLAY_34("overlay34"),
        OVERLAY_35("overlay35");

        // This fileName matches up with names used to define the overlays (as found in pmdsky-debug) by HOOPA
        // which is just the name of the symbol/header file for the given overlay
        public final String fileName;

        private Overlay(String fileName) {
            this.fileName = fileName;
        }

    }


    // Okay.
    // Okay, fine.
    // Let it be known! Let it be known, Happylappy as my witness, I tried.
    // I TRIED to do this the nice way
    // but NOOOOOOO, gson doesn't WANT to write to the file properly
    // and there isn't even an error message! I can *only* assume it's due to the volume of the data being parsed through
    // so, fine. We're doing this the hard way.
    /*
    public class DefinedAddress {
        public String label;
        public String address;
        public Overlay containingOverlay;
        public Region region;
    }

    public class DataDefinition extends DefinedAddress {
        public String heldData;
        public int length;
    }

    public class FunctionDefinition extends DefinedAddress {
        public String returnType;
        public ArrayList<String> args;
    }
    */


	@Override
	protected void run() throws Exception {
    	println("Sample script!");


        Writer writer = new FileWriter("/Users/itred/Desktop/Programming/Active_Projects/pmdsky-debug-HOOPA/src/ghidra/ghidra_scripts/test.json");
        
        JsonWriter jsonWriter = new JsonWriter(writer);
        jsonWriter.setFormattingStyle(FormattingStyle.PRETTY);
        jsonWriter.beginObject();
        

        /*
        MemoryBlock[] blocks = mem.getBlocks();
        
        for (MemoryBlock block : blocks) {
            //println(block);
        }
        */
        
        Memory programMemory = currentProgram.getMemory();
        AddressRangeIterator memoryIterator = programMemory.getAddressRanges();

        
        while (memoryIterator.hasNext()) {

            AddressRange blockAddressRange = memoryIterator.next();
            Iterator<Address> addressIterator = blockAddressRange.iterator();

            jsonWriter
                .name(String.valueOf(blockAddressRange.getMinAddress().toString()))
                .beginObject()
                .name("data")
                .beginArray();

            while (addressIterator.hasNext()) {

                Address currentAddress = addressIterator.next();

                Data data = getDataAt(currentAddress);
                Symbol symbol = getSymbolAt(currentAddress);

                if (symbol != null && data != null) {
                    
                    // SourceType.ANALYSIS can sometimes include symbols named automatically (i.e., veneers are named the same as their wrapped function by default)
                    // so we filter only for USER_DEFINED and IMPORTED symbols, since I *think* that's the only ones we care about
                    SourceType source = symbol.getSource();
                    if (source != SourceType.USER_DEFINED && source != SourceType.IMPORTED ) continue; 

                    jsonWriter
                        .beginObject()
                            .name("label")
                                .value(symbol.getName())
                            .name("address")
                                .value(currentAddress.toString())
                            .name("type")
                                .value(data.getDataType().getName())
                            .name("length")
                                .value(data.getLength())
                        .endObject();                   

                }
                
                
            }
            
            jsonWriter.endArray();

            Iterator<Address> addressIterator2 = blockAddressRange.iterator();

            jsonWriter.name("functions")
                .beginArray();

            while (addressIterator2.hasNext()) {

                Address currentAddress = addressIterator2.next();

                Function function = getFunctionAt(currentAddress);
                if (function != null) {
                    
                    // Same as above
                    SourceType source = function.getSignatureSource();
                    if (source != SourceType.USER_DEFINED && source != SourceType.IMPORTED ) continue; 

                    jsonWriter
                        .beginObject()
                            .name("label")
                                .value(function.getName())
                            .name("address")
                                .value(currentAddress.toString())
                            .name("return_type")
                                .value(function.getReturn().getDataType().getName()) // I know it seems kinda cursed, but nothing in this call chain is marked as nullable, so im just gonna take its word for it!
                            .name("args")
                                .beginArray();
                                    
                    if (function.getParameters() != null) {
                        for (Parameter param : function.getParameters()) {
                            
                            jsonWriter.beginObject()
                                .name("label")
                                    .value(param.getName())
                                .name("type")
                                    .value(param.getDataType().getName())
                            .endObject();

                        }
                    }
                    
                    jsonWriter.endArray()
                        .endObject();
                    
                }
            }

            jsonWriter.endArray()
                .endObject();
        }
             
        jsonWriter.endObject();

        jsonWriter.close();

	}
    

    

    
}
