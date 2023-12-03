import struct

def to_float(int_value):
    # Use struct to interpret the integer as a float
    return struct.unpack('!f', struct.pack('!I', int_value))[0]

def process_analogs(a1, a2):
    # Combine the two 16-bit values into one 32-bit integer
    i32 = (a1 << 16) | a2
    # Convert the 32-bit integer to a float
    rval = to_float(i32)
    # Round to 1 decimal place
    rval = round(rval, 1)
    print("rval", rval)

    data1 = []
    if rval > 0:
        data1.append(['Verdichter', rval, analogs[441]])
    else:
        print('Verdichter no push')

    return data1

# Usage example:
analogs = [0] * 446  # Assuming analogs is a list with at least 446 elements
analogs[444] = 17728 # Your value for analogs[444]
analogs[445] = 28184 # Your value for analogs[445]
analogs[441] = 123 # Your value for analogs[441]

data1 = process_analogs(analogs[444], analogs[445])