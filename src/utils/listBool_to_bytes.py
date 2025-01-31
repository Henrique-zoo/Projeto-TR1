def listBool_to_bytes(listBool):
    """
    Convert a list of boolean values to a byte array.
    """
    return bytes([int(''.join(['1' if x else '0' for x in listBool[i:i+8]]), 2) for i in range(0, len(listBool), 8)])