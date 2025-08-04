# EcuCalSrecA2L

A Python utility for automotive ECU calibration, enabling parsing and modification of Motorola S-record (SREC) and A2L files. Supports reading and updating parameter values, with planned features for a command-line interface and Excel import/export.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from ecucalsreca2l.parser import SrecA2LParser

parser = SrecA2LParser('path/to/firmware.mot', 'path/to/ecu.a2l', byte_order='big')
value = parser.get_parameter_value('SnsrPLo_FilTiCon')
print(f"Value: {value}")
parser.set_parameter_value('SnsrPLo_FilTiCon', 50.0)
parser.save_srec('path/to/modified_firmware.mot')
```

## Future Features

* Command-line interface for batch processing parameters.
* Export/import parameter data to/from Excel using Pandas.