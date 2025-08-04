import struct
from a2lparser.a2lparser import A2LParser
from hexformat.srecord import SRecord
from typing import Dict, Any, Union, List
import pandas as pd
from .format_map import A2L_FORMAT_MAP
# from .format_map import A2L_FORMAT_MAP
# A2L_FORMAT_MAP = {
#     'UBYTE': {'format': 'B', 'length': 1},           # Unsigned 8-bit
#     'SBYTE': {'format': 'b', 'length': 1},           # Signed 8-bit
#     'UWORD': {'format': 'H', 'length': 2},           # Unsigned 16-bit
#     'SWORD': {'format': 'h', 'length': 2},           # Signed 16-bit
#     'ULONG': {'format': 'I', 'length': 4},           # Unsigned 32-bit
#     'SLONG': {'format': 'i', 'length': 4},           # Signed 32-bit
#     'FLOAT32_IEEE': {'format': 'f', 'length': 4},    # 32-bit float
#     'FLOAT64_IEEE': {'format': 'd', 'length': 8}     # 64-bit double
# }

class SrecFileParser:
    """Class to parse and modify ECU firmware SREC and A2L files."""
    
    def __init__(self, srec_path: str, a2l_path: str, byte_order: str = 'big'):
        """Initialize with SREC and A2L file paths and byte order."""
        if byte_order not in ['big', 'little']:
            raise ValueError("byte_order must be 'big' or 'little'")
        self.byte_order = byte_order
        self.endian_prefix = '>' if byte_order == 'big' else '<'
        self.srec_path = srec_path
        self.a2l_path = a2l_path
        self.srec = self._parse_srec_file()
        self.chars_dict, self.record_layout_dict = self._parse_a2l_file()
    
    def _parse_srec_file(self) -> SRecord:
        """Parse an SREC file and return the SRecord object."""
        return SRecord.fromfile(self.srec_path)
    
    # @staticmethod
    def get_a2l_datatype(self,var) -> str:
        # data_type = "_".join(var['Deposit_Ref'].split('_')[1:]) 
        # Map Deposit_Ref to Datatype using RECORD_LAYOUT
        deposit_ref = var['Deposit_Ref']
        if deposit_ref not in self.record_layout_dict:
            raise ValueError(f"Record layout {deposit_ref} not found in A2L file")
        data_type = self.record_layout_dict[deposit_ref]
        if data_type not in A2L_FORMAT_MAP:
            raise ValueError(f"Unsupported data type: {data_type}")
        return data_type
    
    def _parse_a2l_file(self) -> Dict[str, Any]:
        """Parse an A2L file and return a dictionary of characteristics."""
        ast_dict = A2LParser(quiet=True).parse_file(self.a2l_path)
        a2l = list(ast_dict.values())[0]
        chars = a2l.find_sections("CHARACTERISTIC")['CHARACTERISTIC']
        chars_dict = {ch['Name']: ch for ch in chars}
        
        # Extract RECORD_LAYOUT section
        record_layouts = a2l.find_sections("RECORD_LAYOUT")['RECORD_LAYOUT']
        record_layout_dict = {
            rl['Name']: rl['FNC_VALUES']['Datatype']
            for rl in record_layouts
            if 'FNC_VALUES' in rl and 'Datatype' in rl['FNC_VALUES']
        }
        
        return chars_dict, record_layout_dict
    

    
    def get_parameter_value(self, var_name: str) -> Union[Any, List[Any]]:
        """Extract parameter value(s) from SREC data based on A2L data type and NUMBER."""
        if var_name not in self.chars_dict:
            raise ValueError(f"Parameter {var_name} not found in A2L file")
        
        var = self.chars_dict[var_name]
        address = var['Address']
        deposit_ref = var['Deposit_Ref']
        
        # Map Deposit_Ref to Datatype using RECORD_LAYOUT
        if deposit_ref not in self.record_layout_dict:
            raise ValueError(f"Record layout {deposit_ref} not found in A2L file")
        data_type = self.record_layout_dict[deposit_ref]
        
        if data_type not in A2L_FORMAT_MAP:
            raise ValueError(f"Unsupported data type: {data_type}")
        
        length = A2L_FORMAT_MAP[data_type]['length']
        format_spec = A2L_FORMAT_MAP[data_type]['format']
        
        # Check for vector (NUMBER field)
        num_elements = int(var.get('NUMBER', '1'))  # Default to 1 if NUMBER is absent
        if num_elements < 1:
            raise ValueError(f"Invalid NUMBER value for {var_name}: {num_elements}")
        
        total_length = length * num_elements
        format_spec = f"{self.endian_prefix}{num_elements}{format_spec}"
        
        try:
            data = self.srec.get(int(address, 16), total_length)
            values = struct.unpack_from(format_spec, data)
            return list(values) if num_elements > 1 else values[0]
        except Exception as e:
            raise ValueError(f"Error extracting value at address {address}: {str(e)}")
    
    def set_parameter_value(self, var_name: str, value: Union[Any, List[Any]]) -> None:
        """Set parameter value(s) in SREC data based on A2L data type and NUMBER."""
        if var_name not in self.chars_dict:
            raise ValueError(f"Parameter {var_name} not found in A2L file")
        
        var = self.chars_dict[var_name]
        address = var['Address']
        deposit_ref = var['Deposit_Ref']
        
        # Map Deposit_Ref to Datatype using RECORD_LAYOUT
        if deposit_ref not in self.record_layout_dict:
            raise ValueError(f"Record layout {deposit_ref} not found in A2L file")
        data_type = self.record_layout_dict[deposit_ref]
        
        if data_type not in A2L_FORMAT_MAP:
            raise ValueError(f"Unsupported data type: {data_type}")
        
        length = A2L_FORMAT_MAP[data_type]['length']
        format_spec = A2L_FORMAT_MAP[data_type]['format']
        
        # Check for vector (NUMBER field)
        num_elements = int(var.get('NUMBER', '1'))  # Default to 1 if NUMBER is absent
        if num_elements < 1:
            raise ValueError(f"Invalid NUMBER value for {var_name}: {num_elements}")
        
        # Validate input value
        if num_elements > 1:
            if not isinstance(value, (list, tuple)) or len(value) != num_elements:
                raise ValueError(f"Expected a list of {num_elements} values for {var_name}, got {value}")
        else:
            if isinstance(value, (list, tuple)):
                raise ValueError(f"Expected a single value for {var_name}, got a list: {value}")
        
        total_length = length * num_elements
        format_spec = f"{self.endian_prefix}{num_elements}{format_spec}"
        
        try:
            data = struct.pack(format_spec, *value) if num_elements > 1 else struct.pack(format_spec, value)
            self.srec.set(int(address, 16), data)
        except Exception as e:
            raise ValueError(f"Error setting value at address {address}: {str(e)}")
    
    def save_srec(self, output_path: str) -> None:
        """Save the modified SREC file."""
        try:
            self.srec.tofile(output_path)
            print(f"Modified SREC file saved to {output_path}")
        except Exception as e:
            raise ValueError(f"Error saving SREC file: {str(e)}")
        
    def export_parameters_to_excel(self, output_excel: str) -> None:
        data = []
        for var_name, var in self.chars_dict.items():
            value = self.get_parameter_value(var_name)
            data.append({
                'Name': var_name,
                'Address': var['Address'],
                'Type': var['Deposit_Ref'],
                'Value': value
            })
        df = pd.DataFrame(data)
        if output_excel.endswith('.xlsx'):
            df.to_excel(output_excel, index=False)
        
        if output_excel.endswith('.csv'):
            df.to_csv(output_excel, index=False)
            
        print(f"Parameters exported to {output_excel}")
        
    

    def import_parameters_from_excel(self, input_excel: str) -> None:
        df = pd.read_excel(input_excel)
        for _, row in df.iterrows():
            var_name = row['Name']
            value = row['Value']
            if var_name in self.chars_dict:
                self.set_parameter_value(var_name, value)
            
# def main():
#     # File paths
#     srec_path = r'data\MOT_CAL_FILE.mot'
#     a2l_path = r'data\A2L_MAP_FILE.a2l'
#     output_srec_path = r'data\export\MOT_CAL_FILE_modified.mot'
    
#     # Parameter to process
#     var_name = 'SnsrPLo_FilTiCon'
#     byte_order = 'big'  # Options: 'big' or 'little'
    
#     try:
#         # Initialize parser with specified byte order
#         parser = SrecA2lParser(srec_path, a2l_path, byte_order=byte_order)
        
#         # Extract current value
#         value = parser.get_parameter_value(var_name)
#         print(f"Parameter {var_name} at address {parser.chars_dict[var_name]['Address']}, "
#               f"type: {parser.chars_dict[var_name]['Deposit_Ref']}, value: {value}")
        
#         # Example: Modify the parameter value (e.g., set to 50.0)
#         new_value = 50.0
#         # parser.set_parameter_value(var_name, new_value)
#         # print(f"Updated {var_name} to {new_value}")
        
#         # # Save modified SREC file
#         # parser.save_srec(output_srec_path)
    
#     except Exception as e:
#         print(f"Error: {str(e)}")

# if __name__ == '__main__':
#     main()