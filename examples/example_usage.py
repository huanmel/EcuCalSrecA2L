import sys
import os
# Add the src/ directory to sys.path
# for case usage without installation
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from SrecFileUtils.srec_a2l_parser import SrecFileParser

def main():
    srec_path = r'data\MOT_CAL_FILE.mot'
    a2l_path = r'data\A2L_MAP_FILE.a2l'
    output_srec_path = r'data\export\MOT_CAL_FILE_modified.mot'
    var_name = 'SnsrTBattCoolt_RMapX'
    byte_order = 'big'
    
    try:
        parser = SrecFileParser(srec_path, a2l_path, byte_order=byte_order)
        value = parser.get_parameter_value(var_name)
        print(f"Parameter {var_name} at address {parser.chars_dict[var_name]['Address']}, "
              f"type: {parser.chars_dict[var_name]['Deposit_Ref']}, value: {value}")
        # new_value = 50.0
        # parser.set_parameter_value(var_name, new_value)
        # print(f"Updated {var_name} to {new_value}")
        # parser.save_srec(output_srec_path)
        parser.export_parameters_to_excel('data\export\parameters.xlsx')
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    main()