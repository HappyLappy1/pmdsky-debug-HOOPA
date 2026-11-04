
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.Reader;
import java.io.Writer;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.stream.Stream;

import com.formdev.flatlaf.json.Json;
import com.google.gson.FormattingStyle;
import com.google.gson.Gson;
import com.google.gson.stream.JsonReader;
import com.google.gson.stream.JsonWriter;

import ghidra.app.script.GhidraScript;
import ghidra.app.util.ColorAndStyle;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.util.CodeUnitInsertionException;
import ghidra.util.exception.CancelledException;
import ghidra.util.exception.DuplicateNameException;
import ghidra.util.exception.InvalidInputException;
import ghidra.program.model.address.AddressRangeIterator;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DataTypeManager;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.symbol.SourceType;

import java.awt.Color;


public class StringIDParser extends GhidraScript {

    private static final String STRING_ID_DATATYPE = "uint32_t";
    private static final String STRING_ID_DATATYPE_ALT = "undefined4";

    private static final String STRING_ID_LABEL = "STRING_ID_<RENAMEHERE>";
    /*
    String ID <decimal> (<hex>):
    "<contents>"
    */
    private static final String STRING_ID_COMMENT_FORMAT = "String ID %d (%s):\n\"%s\"";

    private static final int STRING_ID_LIMIT = 18451;  

    private void printErrorMessage(String message) {
        println("StringIDParser - ERROR: " + message, new Color(200, 100, 100));
    }

    private String getTextStringWithIDFromCache(File cache, long ID) throws IOException, IndexOutOfBoundsException {

        if (ID > STRING_ID_LIMIT) throw new IndexOutOfBoundsException("Selected data could not possibly be a string ID! (out of bounds)");

        try (FileReader reader = new FileReader(cache)) {
            JsonReader jsonReader = new JsonReader(reader);
            
            
            jsonReader.beginArray();
            while (ID > 1 && jsonReader.hasNext()) {
                ID--;
                jsonReader.skipValue();
            }
            
            String foundString = jsonReader.nextString();
            jsonReader.close();
            return foundString;
        }
    }

    private void setStringIDCommentAndLabel(Address address, Symbol symbol, Data data, String textString, long stringID) throws DuplicateNameException, InvalidInputException, CancelledException, CodeUnitInsertionException {

        if (getPlateComment(address) != null) {
            boolean result = askYesNo("Heads up!", "There's already an existing plate comment on the field " + address.toString() + ". Are you sure you want to overwrite it?");
            if (!result) {
                println("Cancelling operation...");
                return;
            };
        }

        if (symbol.getSource() != SourceType.DEFAULT) {
            boolean result = askYesNo("Heads up!", "There's already an existing non-default label on the field "  + address.toString() + ". Are you sure you want to overwrite it?");
            if (!result) {
                println("Cancelling operation...");
                return;
            };
        }

        if (data.getDataType().getName() != STRING_ID_DATATYPE) {
            
            // Find the uint32_t datatype to set the value to. There's only ever one of this exact name, but it can be a bit buried
            ArrayList<DataType> typeList = new ArrayList<>();
            DataTypeManager manager = currentProgram.getDataTypeManager();
            manager.findDataTypes(STRING_ID_DATATYPE, typeList);

            // If im not terribly mistaken, we'll *always* have only one item, and it'll *always* be the nds uint32_t.
            // I hope.
            DataType uint32_t = typeList.get(0);
            clearListing(address);
            createData(address, uint32_t);

        }
       
        

        // Have to do it this way, since formatting with "%#X" also capitalizes the 'x' in '0x'
        String stringIDHex = "0x" + String.format("%X", stringID);
        String formattedPlateComment = String.format(STRING_ID_COMMENT_FORMAT, stringID, stringIDHex, textString);
        setPlateComment(address, formattedPlateComment);
        symbol.setName(STRING_ID_LABEL, SourceType.USER_DEFINED);
        
        

    }


    @Override
    protected void run() throws Exception {
        
        File file = askFile("Select text-strings json file", "GO");
        
        
        Data currentData = getDataAt(currentAddress);
        Symbol currentSymbol = getSymbolAt(currentAddress);

        if (currentSymbol == null) {
            printErrorMessage("You must select a symbol first!");
            return;
        }

        if (currentData == null) {
            printErrorMessage("Selected symbol does not contain data!");
            return;
        }

        if ( !(currentData.getDataType().getName().equals(STRING_ID_DATATYPE) || currentData.getDataType().getName().equals(STRING_ID_DATATYPE_ALT) )) {
            printErrorMessage("Selected symbol is of an incorrect datatype! For safety, type it as a " + STRING_ID_DATATYPE + " or a " + STRING_ID_DATATYPE_ALT + ", first.");
            return;
        }

        long stringID = currentData.getUnsignedInt(0);
        String textString = getTextStringWithIDFromCache(file, stringID);
        setStringIDCommentAndLabel(currentAddress, currentSymbol, currentData, textString, stringID);

    }
    
}
