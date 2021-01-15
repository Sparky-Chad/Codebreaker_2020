import numpy as np
from bitstring import BitArray
from run_hamming import remove_buffer
import Hamming_System
import utils
import os


"""
Class for inputing results into
"""

class results():
    def __init__(self, output_name="hamming_record.txt"):
        # Write and clear file
        f = open(output_name, 'w')
        f.close()

        self.file = output_name
        # Now we can append when writing

    def write(self, polynomial, matrix):
        with open(self.file, 'a') as f:
            f.write('-' *30+'\n')
            f.write('\nPolynomial:\n'+np.array2string(polynomial, separator=',')+'\n')
            f.write('Parity Check Matrix:\n'+np.array2string(matrix, separator=',')+'\n')
            f.write('-'*30+'\n'+'*'*30+'\n')

def mass_decode(filename = "decoded.ham"):
    # instantiate r and list of possible block sizes
    binary = BitArray(filename=filename).bin
    r = 2
    list_blocks = []
    report = results()
    for i in range(3, int(len(binary)/4)):
        if 2**r - 1 < i:
            r += 1
        if len(binary) / i * (i-r) % 8 == 0 and len(binary) % i == 0:
            list_blocks.append(i)

    # setup binary to np array
    binary = np.array(list(map(lambda x: ord(x) - 48, binary)),dtype=int)
    for i in list_blocks:
        for ham,rev in Hamming_System.Hamming_Codes(i,check_reversed=True):
            #+'0'*(ham._block_siz e- (len(deci)%ham._block_size))
            decode = None
            try:
                # decode and then digest into a seperate file
                decode = ham.decode(np.array(binary, dtype=int))
            except Hamming_System.HammingDoubleBitError:
                continue
            decode = BitArray(bin=''.join(list(map(lambda x: chr(x+48), decode.tolist()))))
            decode = remove_buffer(decode[:len(decode)-(len(decode)%8)])

            if rev:
                filename= './decoded/video_rev_file'+str(ham.parity_length)+''.join(list(map(lambda x: chr(x + 48),ham.poly.tolist()))) + '.vid'
            else:
                filename= './decoded/video_file'+str(ham.parity_length)+''.join(list(map(lambda x: chr(x + 48),ham.poly.tolist()))) + '.vid'
            ham.digest(filename)

            if rev:
                filename= './decoded/video_rev_nobuffer_file'+str(ham.parity_length)+''.join(list(map(lambda x: chr(x + 48),ham.poly.tolist()))) + '.vid'
            else:
                filename= './decoded/video_nobuffer_file'+str(ham.parity_length)+''.join(list(map(lambda x: chr(x + 48),ham.poly.tolist()))) + '.vid'
            decode.tofile(open(filename, 'wb'))
            # Now open file and append data
            report.write(ham.poly, ham.H)
    print("done")

def decode(filename = "decoded.ham"):
    # instantiate r and list of possible block sizes
    binary = BitArray(filename=filename).bin
    r = 2
    list_blocks = []
    report = results()
    for i in range(2, 14):
        r = 2**i - 1
        if len(binary) % r == 0:
            list_blocks.append(i)

    # setup binary to np array
    deci = binary
    
    for i in list_blocks:
        for ham, rev in Hamming_System.Hamming_Codes(2**i-1,check_reversed=True):
            #+'0'*(ham._block_siz e- (len(deci)%ham._block_size))
            binary = np.array(list(map(lambda x: ord(x) - 48, deci)),dtype=int)
            decode = None
            print(ham.H)
            try:
                # decode and then digest into a seperate file
                decode = ham.decode(np.array(binary, dtype=int))
            except Hamming_System.HammingDoubleBitError:
                continue
            decode = BitArray(bin=''.join(list(map(lambda x: chr(x+48), decode.tolist()))))
            #decode = remove_buffer(decode[:len(decode)-(len(decode)%8)])

            if rev:
                filename= './decoded/video_rev_file'+str(ham.parity_length)+''.join(list(map(lambda x: chr(x + 48),ham.poly.tolist()))) + '.vid'
            else:
                filename= './decoded/video_file'+str(ham.parity_length)+''.join(list(map(lambda x: chr(x + 48),ham.poly.tolist()))) + '.vid'
            ham.digest(filename)

            if rev:
                filename= './decoded/video_rev_nobuffer_file'+str(ham.parity_length)+''.join(list(map(lambda x: chr(x + 48),ham.poly.tolist()))) + '.vid'
            else:
                filename= './decoded/video_nobuffer_file'+str(ham.parity_length)+''.join(list(map(lambda x: chr(x + 48),ham.poly.tolist()))) + '.vid'
            decode.tofile(open(filename, 'wb'))
            # Now open file and append data
            report.write(ham.poly, ham.H)
    print("done")
if __name__ == "__main__":
    os.system("rm ./decoded/*")
    mass_decode()
