import sys
import os
import argparse
from typing import List, Union

# Add src/ directory to sys.path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if not os.path.exists(src_path):
    raise FileNotFoundError(f"Source directory not found: {src_path}")
sys.path.append(src_path)

try:
    from SrecFileUtils.srec_a2l_parser import SrecFileParser

except ImportError as e:
    print(f"ImportError: {e}")
    print(f"sys.path: {sys.path}")
    raise

def parse_vector_value(value_str: str, num_elements: int) -> List[float]:
    """Parse a comma-separated string into a list of floats, validating length."""
    try:
        values = [float(v) for v in value_str.split(',')]
        if len(values) != num_elements:
            raise ValueError(f"Expected {num_elements} values, got {len(values)}")
        return values
    except ValueError as e:
        raise ValueError(f"Invalid value format: {value_str}. Expected {num_elements} comma-separated numbers.") from e

def main():
    parser = argparse.ArgumentParser(description="EcuCalSrecA2L CLI for ECU calibration")
    parser.add_argument('action', choices=['get', 'set'], help="Action to perform (get or set parameter)")
    parser.add_argument('--var', required=True, help="Parameter name (e.g., SnsrPLo_FilTiCon)")
    parser.add_argument('--srec', required=True, help="Path to SREC file")
    parser.add_argument('--a2l', required=True, help="Path to A2L file")
    parser.add_argument('--value', help="New value(s) for set action (single number for scalar, comma-separated for vector)")
    parser.add_argument('--output', help="Output SREC file path for set action")
    parser.add_argument('--byte-order', default='big', choices=['big', 'little'], help="Byte order (default: big)")
    
    args = parser.parse_args()

    # Validate file paths
    for path in [args.srec, args.a2l]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

    # Initialize parser
    try:
        sreca2l_parser = SrecFileParser(args.srec, args.a2l, byte_order=args.byte_order)
    except Exception as e:
        print(f"Error initializing parser: {str(e)}")
        sys.exit(1)

    # Get number of elements for the parameter
    try:
        num_elements = int(sreca2l_parser.chars_dict.get(args.var, {}).get('NUMBER', '1'))
    except ValueError as e:
        print(f"Error: Invalid NUMBER value for {args.var}")
        sys.exit(1)

    if args.action == 'get':
        try:
            value = sreca2l_parser.get_parameter_value(args.var)
            print(f"{args.var}: {value}")
        except Exception as e:
            print(f"Error getting value for {args.var}: {str(e)}")
            sys.exit(1)
    
    elif args.action == 'set':
        if args.value is None or args.output is None:
            parser.error("set action requires --value and --output")
        
        try:
            # Parse value based on whether it's a scalar or vector
            if num_elements > 1:
                value = parse_vector_value(args.value, num_elements)
            else:
                value = float(args.value)
            
            sreca2l_parser.set_parameter_value(args.var, value)
            sreca2l_parser.save_srec(args.output)
            print(f"Updated {args.var} to {value} and saved to {args.output}")
        except Exception as e:
            print(f"Error setting value for {args.var}: {str(e)}")
            sys.exit(1)

if __name__ == '__main__':
    main()
