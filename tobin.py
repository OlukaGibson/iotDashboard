from intelhex import IntelHex

def hex_to_bin(hex_file_path, bin_file_path):
    # Create an IntelHex object
    ih = IntelHex(hex_file_path)
    
    # Write to a binary file
    ih.tobinfile(bin_file_path)
    print(f"Converted {hex_file_path} to {bin_file_path}.")

hex_file_path = "AirQo-Grev6B-V42_only_6B3.ino.mega.hex" 
bin_file_path = "output.bin" 

hex_to_bin(hex_file_path, bin_file_path)
