# Global format map with base format specifiers and byte lengths
A2L_FORMAT_MAP = {
    'UBYTE': {'format': 'B', 'length': 1},           # Unsigned 8-bit
    'SBYTE': {'format': 'b', 'length': 1},           # Signed 8-bit
    'UWORD': {'format': 'H', 'length': 2},           # Unsigned 16-bit
    'SWORD': {'format': 'h', 'length': 2},           # Signed 16-bit
    'ULONG': {'format': 'I', 'length': 4},           # Unsigned 32-bit
    'SLONG': {'format': 'i', 'length': 4},           # Signed 32-bit
    'FLOAT32_IEEE': {'format': 'f', 'length': 4},    # 32-bit float
    'FLOAT64_IEEE': {'format': 'd', 'length': 8}     # 64-bit double
}