# EcuCalSrecA2L

A Python utility for automotive ECU calibration, enabling parsing and modification of Motorola S-record (SREC) and A2L files. Supports reading and updating parameter values, with planned features for a command-line interface and Excel import/export.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from SrecFileUtils.srec_a2l_parser import SrecFileParser

srec_path = r'data\MOT_CAL_FILE.mot'
a2l_path = r'data\A2L_MAP_FILE.a2l'
output_srec_path = r'data\export\MOT_CAL_FILE_modified.mot'
var_name = 'SnsrTBattCoolt_RMapX'
byte_order = 'big'
parser = SrecFileParser(srec_path, a2l_path, byte_order=byte_order)
value = parser.get_parameter_value(var_name)
print(f"Parameter {var_name} at address {parser.chars_dict[var_name]['Address']}, "
f"type: {parser.chars_dict[var_name]['Deposit_Ref']}, value: {value}")
new_value = 50.0
parser.set_parameter_value(var_name, new_value)
print(f"Updated {var_name} to {new_value}")
parser.save_srec(output_srec_path)
parser.export_parameters_to_excel('data\export\parameters.xlsx')
```

## Future Features

* Command-line interface for batch processing parameters.
* Export/import parameter data to/from Excel using Pandas.