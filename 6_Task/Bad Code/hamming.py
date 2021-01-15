import numpy as np
from functools import reduce
from math import floor
import operator as op
from bitstring import BitArray
from time import sleep


# Assumes the input will be an already enumerated array which this can then check
"""
def decode_hamming(input):
    int_input = list(map(lambda x: ord(x)-48, input))
    print((int_input))
    err_position = reduce(op.xor, [i for i, bit in enumerate(int_input[:15]) if bit])
    if (err_position != 0):
        print(err_position)
        # test if there are two errors, the return should allow me to find out why
        #if(reduce(op.xor, [i for i, bit in enumerate(int_input) if bit]) == int_input[15]):
        #        raise TypeError(f'Wrong hamming type which resulted in error: {input}')
        # bitwise xor acts as swapper if 1 then is 0 and otherwise is 1
        int_input[err_position - 1] = not int_input[err_position - 1]
        # recreate input bit string
        input = list(map(lambda x: chr(x + 48), int_input))

    data = [input[2],''.join(input[4:7]), ''.join(input[8:15])] 
    data = ''.join(data)
    return data
"""
class HammingError(Exception):
    pass

# This function will take corrected hamming code, and output a string litteral
# of data
def decode_data(input, r=1):
    data = ""
    if(r == 1):
        while( 2**r <= len(input)):
            r += 1
    for i in range(1, r-1):
        data += ''.join(input[2**i:2**(i+1) - 1])
    return data


def correct_err(input, r=1):
    if(r == 1):
        while(2**r <= len(input)):
            r += 1
    int_input = list(map(lambda x: ord(x)-48, input))

    enum = [i for i, bit in enumerate(int_input[:len(int_input)-1]) if bit]
    if len(enum) == 0:
        data = []
        for i in range(2**r - r -1):
            data.append('0')
            return ''.join(data)

    err_position = reduce(op.xor, [i for i, bit in enumerate(int_input[:len(int_input)-1]) if bit])
    if(err_position != 0):
        # This finds if two errors have ocurred
        if(0 == reduce(op.xor, int_input)):
            raise HammingError(f"Wrong hamming type which resulted in error: {''.join(input)}")
        print(err_position, ' ', (len(int_input)), ' ', ''.join(input))
        # Correct error and reformat input
        int_input[err_position - 1] = not int_input[err_position - 1]
        input = list(map(lambda x: chr(x + 48), int_input))

    # return data as a string format
    return decode_data(input, r)


# Generator will return numbers depending on what numbers are given to it
# will essential yield a tuple of (i, 0) and (i, 1) to represent reversed 
# and not reversed 
def permutate(num):
    assert type(num) is range

    for i in num:
        yield (int(2**i / 8), 0,i)

        yield (int(2**i / 8), 1,i)

def main():
    output = ''
    # modify the number of bytes being stored
    for i in permutate(range(3,5)):
        try:
            with open("decoded.ham", 'rb') as f:
                while True:
                    cur_bytes = f.read(i[0])
                    if(len(cur_bytes) < i[0]):
                        raise EOFError("Reached end of File prematurely")
                    bitstring = list(BitArray(cur_bytes).bin)
                    #if(sum(list(int(i,2) for i in bitstring)) == 0):
                        #continue
                    #print(bitstring)
                    if (i[1]):
                        output += correct_err(bitstring[::-1],i[2])[::-1]
                    else:
                        output += correct_err(bitstring,i[2])
            with open("signal.decoded", 'w') as f:
                f.writelines(output)
                return
        except HammingError as error:
            print(error)
            sleep(5)
            continue


if ( __name__ == "__main__"):
    main()
