import matplotlib.pyplot as plt
import numpy as np
import bitstring
from math import isnan
from utils import Progress
from os.path import getsize


def float_from_unsigned16(n):
    assert 0 <= n < 2**16
    sign = n >> 15
    exp = (n >> 10) & 0b011111
    fraction = n & (2**10 - 1)
    if exp == 0:
        if fraction == 0:
            return -0.0 if sign else 0.0
        else:
            return (-1)**sign * fraction / 2**10 * 2**(-14)  # subnormal
    elif exp == 0b11111:
        # Must only worry about the sign to make it a negative or a positive
        # Might think about not doing this later
        return -1.0 if sign else 1
        if fraction == 0:
            return float('-inf') if sign else float('inf')
        else:
            return float('nan')
        
    return (-1)**sign * (1 + fraction / 2**10) * 2**(exp - 15)

def create_data(filename):
    dat = []
    prog = Progress("Reading File", int(getsize(filename)))
    count = 0
    with open(filename, 'rb') as f:
        while True:
            # Read Raw bytes from file to ndarray to allow for byteswap
            bit = f.read(2)
            if len(bit) == 0:
                break
            bits = np.ndarray(shape=(1,),dtype='>u2',buffer=bit).byteswap()
            temp = (float_from_unsigned16(int(bits[0])))
            count += 2
            if isnan(temp):
                print(f"isnan: {temp} : {bit} : {count}")
                continue
            dat.append(temp)
            if count % 0x1e00 == 0:
                prog.print(count)
    return dat

def gen_little_data(filename):
    dat = []
    prog = Progress("Reading File", int(getsize(filename)))
    count = 0
    with open(filename, 'rb') as f:
        while True:
            # Read bytes from file to ndarray, swap bits to little then repack into uint16
            bit = f.read(2)
            if len(bit) == 0:
                break
            bits = np.unpackbits(np.ndarray(shape=(2,),dtype=np.uint8, buffer=bit),bitorder="little")
            bits = np.ndarray(shape=(1), dtype='>u2',buffer=np.packbits(bits))
            temp = (float_from_unsigned16(int(bits[0])))
            count+=2
            if isnan(temp):
                print(f"isnan: {temp} : {bit} : {count}")
            dat.append(temp)
            if count % 0x1e00 == 0:
                prog.print(count)
    return dat

def generate_other(dat):
    x = np.arange(0,len(dat),1)
    bit0, bit1 = [],[]
    for i,j in zip(dat, x):
        bit1.append(abs(i) * np.cos(np.pi*j))
        bit0.append( (abs(i)*np.cos(np.pi*j+np.pi)))
    return x, bit0, bit1

def plot_data(x, dat, bit0, bit1):
    plt.xlim([6105720,6105740])
    plt.ylim([-2,2])
    plt.plot(x, dat, label="signal")
    #plt.plot(x,bit0, label='cos(pi)')
    #plt.plot(x,bit1, label="-cos(pi)")
    plt.show()


def legacy_gen_data(dat, bit0, bit1):
    bit_buffer = ''
    data = bitstring.BitArray()

    for i in range(0, len(dat)):
        if dat[i] == bit0[i]:
            bit_buffer += '0'
        elif dat[i] == bit1[i]:
            bit_buffer += '1'
        else:
            raise TypeError(f"Error with the value: {i} {dat[i]} {bit0[i]} {bit1[i]}")
        if len(bit_buffer) == 8:
            data.append(bitstring.Bits(bin=bit_buffer))
            bit_buffer = ""
    if len(bit_buffer):
        data.append(bitstring.Bits(bin=bit_buffer))
    return data


def gen_data(dat):
    bit_buffer = ''
    data = bitstring.BitArray()
    prog = Progress("Generating Data", len(dat))
    for i in range(0, len(dat)):
        if dat[i] > 0:
            bit_buffer += '1'
        elif dat[i] < 0:
            bit_buffer += '0'
        else:
            raise TypeError(f"Error in signal value: {i} {dat[i]}")
        if len(bit_buffer) == 8:
            data.append(bitstring.Bits(bin=bit_buffer))
            bit_buffer = ""
        
        
        if i % 0x1ee00 == 0:
            prog.print(i)
            
    if len(bit_buffer):
        data.append(bitstring.Bits(bin=bit_buffer))
    return data


def main():
    dat = create_data("signal.ham")
    #dat = gen_little_data("signal.ham")
    # Now generate plot for matplotlib
    #x, bit0, bit1 = generate_other(dat)
    # This was the plotting stuff to prove this method had merit
    #plot_data(x, dat, bit0, bit1)

    #with open("signal.cf32", 'wb') as f:
    #    for i in np.array(dat).astype(np.float):
    #        f.write(i)
    #data = legacy_gen_data(dat, bit0, bit1)
    #with open("decoded_diff.ham", 'wb') as f:
    #    data.tofile(f)

    data = gen_data(dat)

    with open("decoded.ham", 'wb') as f:
        data.tofile(f)



if __name__ == "__main__":
    main()

