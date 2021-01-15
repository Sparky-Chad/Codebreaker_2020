import numpy as np
from functools import reduce
from math import floor
import operator as op
from bitstring import BitArray
from time import sleep
import scikit_dsp_comm.sk_dsp_comm.fec_block as hamm
from utils import dumphex, permutate_ham,progress_bar,Progress
from signature import check_file
import os

class HammingError(Exception):
    pass
   
# This is the 84 Hamming array which can be used to check the messages
ham_84 = np.array([ [0,1,1,1,1,0,0,0],
                    [1,0,1,1,0,1,0,0],
                    [1,1,0,1,0,0,1,0],
                    [1,1,1,0,0,0,0,1] ])

ham_84_rev = np.array([ [1,0,0,0,0,1,1,1],
                        [0,1,0,0,1,0,1,1],
                        [0,0,1,0,1,1,0,1],
                        [0,0,0,1,1,1,1,0]])

ham_74 = np.array([ [1,0,1,1,1,0,0],
                    [1,1,1,0,0,1,0],
                    [1,1,0,1,0,0,1] ])
ham_74_reg_rev = np.array([
                [1,0,0,1,0,1,1],
                [0,1,0,1,1,1,0],
                [0,0,1,0,1,1,1]])

ham_74_rev = np.array([
                [1,0,0,0,1,1,1],
                [0,1,0,1,0,1,1],
                [0,0,1,1,1,0,1] ])

ham_74_other = np.array([
                [1,1,1,0,1,0,0],
                [0,1,1,1,0,1,0],
                [1,0,1,1,0,0,1]])
# Reversed array
# Syndrome Array Which can be used to find the position of the error
Syndrome_Array = { 
        0: -1,
        15: 0,
        11: 1,
        13:  2,
        14:  3,
        8:  4,
        12:  5,
        10:  6,
        9:  7   }

# Base class of systematic hamming code checker
#
# Will be given R which will allow it to format to allow for different
# parity and message lengths. This class will be able to work for if 
# there is extra parity or not. 
#
# This will instead work to generate non systematic hamming codes 
# from systematic hamming codes
class Hamming_Check():

    def __init__(self, r, extra_parity=True):
        self.r = r
        if extra_parity:
            self.n = 2**(r)
            self.k = self.n - self.r - 1
            self.r += 1 
        else:
            self.n = 2**r - 1
            self.k = 2**r - r - 1
        self.R = np.zeros((self.k, self.n),dtype=int)

        self.syndrome = Syndrome_Array

        self.R[:,:self.k] = np.diag(np.ones(self.k))



class Hamming_84(Hamming_Check):
    def __init__(self,_=None):
        super().__init__(3,True)
        self.H = ham_84
        


    def hamm_decoder(self, codewords):

        if(np.dtype(codewords[0]) != int):
            raise ValueError('Error: Invalid data type, must be vector of ints')

        if(len(codewords) % self.n or len(codewords) < self.n):
            raise ValueError(f'Error: Invalid input vector length length must be multiple of {self.n}')
        decoded_bits = np.zeros(4)

        N_symbols = int(len(codewords)/self.n)

        decoded_bits = np.zeros(N_symbols*self.k)

        codewords = np.reshape(codewords,(1,len(codewords)))

        for i in range(0,N_symbols): 
            # Create error Syndrome
            if(codewords[:,i*self.n:(i+1)*self.n].size == 0):
                break
            S = np.matmul(self.H, codewords[:,i*self.n:(i+1)*self.n].T )%2
            #print(S)
            #print( codewords[:,i*self.n:(i+1)*self.n] )

            # Print S for debugging
            #print(S)

            # Covert Syndrome to integer
            #Bits = ''
            #for m in range(0,len(S)):
            #    bit = str(int(S[m,:]))
            #    Bits = Bits + bit
            #error_pos = self.syndrome[int(Bits,2)]

            # Create array which represents the comparison of columns of S to the
            # Syndrome value, the comparison of which will give the error position
            # which is needed
            #comp = np.all(S == self.H[:,0], axis = 0)
            #h_pos=-1
            #for i in range(np.size(self.H,0)):
            #    if comp[i]:
            #        h_pos = i
            #        break

            #decoded_pos = error_pos
            #print(error_pos, ' : ', int(Bits,2))

            #h_pos=self.H[:,error_pos-1]


            # Use the syndrome to find the position of error within the block
            #bits = ''
            #for m in range(0,len(S)):
            #    bit = str(int(h_pos[m]))
            #    Bits = Bits + bit
            #decoded_pos = int(Bits,2)-1

            """
            This is somewhat unique as we need to match up the syndrome to the correct 
            index. Otherwise this is toast
            """
            decoded_pos = error_pos = self.__match_syndrome__(S)
            # Correct error if present
            if(error_pos != -1):
                codewords[:,i*self.n+decoded_pos]=(codewords[:,i*self.n+decoded_pos]+1)%2

            # Decode the codeword
            decoded_bits[i*self.k:(i+1)*self.k]=np.matmul(self.R, 
                                    codewords[:,i*self.n:(i+1)*self.n].T).T
        return decoded_bits.astype(int)
    
    # Function returns the index the syndrome is pointing to or it will raise an exception
    def __match_syndrome__(self, S):
        if np.sum(S) == 0:
            return -1
            # Run through for loop of each column, this will enable for checking the index
        for j in range(0,self.H.shape[1]):
            # Test if array is the same
            if np.all(S.T == self.H[:,j]):
                return j
        print(S.T)
        raise HammingError("2 Bit error")


class rev_ham_84(Hamming_84):
    def __init__(self,_=None):
        super().__init__()
        self.R = np.zeros((self.k, self.n), dtype=int)
        self.R[:,self.n-self.k:] = np.diag(np.ones(self.k))
        self.H = ham_84_rev

class rev_ham(hamm.fec_hamming):

    # This will have parity checks at the end of the matrix by default. This will allow for hamming codes to be written in either way
    def __init__(self, j):
        super().__init__(j)
        n = 2**j-1
        k = n-j
        self.n, self.k, self.j = n,k,j
        # Create R which is reversed in a way to enable the message to go through
        self.R = np.zeros((self.k, self.n), dtype=int)
        self.R[:,self.n-self.k:] = np.diag(np.ones(self.k))

        # Create H again
        H1 = np.zeros((self.j, self.n-self.k),dtype=int)
        H2 = np.zeros((self.j, self.n-self.j))

        H1[:,:] = self.H[:,self.k:]
        H2[:,:] = self.H[:,:self.k]
        self.H[:,:self.j] = H1
        self.H[:,self.j:] = H2[:,::-1]

"""
    def hamm_decoder(self, codewords):

        if(np.dtype(codewords[0]) != int):
            raise ValueError('Error: Invalid data type, must be vector of ints')

        if(len(codewords) % self.n or len(codewords) < self.n):
            raise ValueError(f'Error: Invalid input vector length length must be multiple of {self.n}')
        decoded_bits = np.zeros(4)

        N_symbols = int(len(codewords)/self.n)

        decoded_bits = np.zeros(N_symbols*self.k)

        codewords = np.reshape(codewords,(1,len(codewords)))

        for i in range(0,N_symbols): 
            # Create error Syndrome
            if(codewords[:,i*self.n:(i+1)*self.n].size == 0):
                break
            S = np.matmul(self.H, codewords[:,i*self.n:(i+1)*self.n].T )%2
            #print(S)
            #print( codewords[:,i*self.n:(i+1)*self.n] )

            # Print S for debugging
            #print(S)

            # Covert Syndrome to integer
            #Bits = ''
            #for m in range(0,len(S)):
            #    bit = str(int(S[m,:]))
            #    Bits = Bits + bit
            #error_pos = self.syndrome[int(Bits,2)]

            # Create array which represents the comparison of columns of S to the
            # Syndrome value, the comparison of which will give the error position
            # which is needed
            #comp = np.all(S == self.H[:,0], axis = 0)
            #h_pos=-1
            #for i in range(np.size(self.H,0)):
            #    if comp[i]:
            #        h_pos = i
            #        break

            #decoded_pos = error_pos
            #print(error_pos, ' : ', int(Bits,2))

            #h_pos=self.H[:,error_pos-1]


            # Use the syndrome to find the position of error within the block
            #bits = ''
            #for m in range(0,len(S)):
            #    bit = str(int(h_pos[m]))
            #    Bits = Bits + bit
            #decoded_pos = int(Bits,2)-1
            
            #This is somewhat unique as we need to match up the syndrome to the correct 
            #index. Otherwise this is toast
            
            decoded_pos = error_pos = self.__match_syndrome__(S)
            # Correct error if present
            if(error_pos != -1):
                codewords[:,i*self.n+decoded_pos]=(codewords[:,i*self.n+decoded_pos]+1)%2

            # Decode the codeword
            decoded_bits[i*self.k:(i+1)*self.k]=np.matmul(self.R, 
                                    codewords[:,i*self.n:(i+1)*self.n].T).T
        return decoded_bits.astype(int)
    
    # Function returns the index the syndrome is pointing to or it will raise an exception
    def __match_syndrome__(self, S):
        if np.sum(S) == 0:
            return -1
            # Run through for loop of each column, this will enable for checking the index
        for j in range(0,self.H.shape[1]):
            # Test if array is the same
            if np.all(S.T == self.H[:,j]):
                return j
        print(S.T)
        raise HammingError("2 Bit error")
"""

def check(filename):
    s = check_file(filename)
    if 'No File' in s:
        print(s)
        print("\n---Continuing---\n")
        sleep(1)
        return False
    else:
        print(s)
        answer = input("Press y to end: ")
        if answer == 'y':
            return True
    return False



def legacy_decode_from_file(filename):
    ham = Hamming_84()
    #byte = None
    #with open(filename, 'rb') as f:
    #    byte = f.read()

    progress_bar('decoding', 34)
    # Create list of char bits for the codewords
    codewords = list(BitArray(filename=filename).bin)

    # Convert list to list of ints
    codewords = list(map(lambda x: ord(x)-48, codewords))

    # Convert to np array
    codewords = np.array(codewords)

    # Decode
    decoded_bits = ham.hamm_decoder(codewords)

    progress_bar('decoding', 58)
    decoded_bits = decoded_bits.tolist()
    decoded_bits = list(map(lambda x: chr(x + 48), decoded_bits))
    return BitArray(bin=''.join(decoded_bits))

def decode_from_file(filename, ham=hamm.fec_hamming(3)):
    # create binary stream from the file
    binary = BitArray(filename="decoded.ham")

    print(ham.H)
    prog = Progress("Decoding")
    prog.print(15)

    # Assert this data is of 7
    #if (len(binary) % 7):
    #    raise ValueError("Data from file is not size of multiple of 7")

    # Create np array in format for the fec_hamming object to read
    codewords = np.array(list(map(lambda x: ord(x)-48, list(binary.bin + '0' * (ham.n - len(binary.bin) % ham.n )))))
    prog.print(38)

    try:
        # Send codewords to be decoded by hamming object
        decoded = ham.hamm_decoder(codewords)
    except HammingError:
        prog.error()
        raise HammingError("2 Bit Error Detected")

    prog.print(64)

    prog.print(100)
    # Convert to bitstring data type and return
    return BitArray(bin=''.join(list(map(lambda x: chr(x + 48), decoded.tolist()))))


def new_buffer(decoded):
    return decoded[:len(decoded)-2]
# Removes the hexadecimal A5
def remove_buffer(decoded):
    progress = Progress("Buffer Removed")
    output = BitArray()
    count = 0x0
    length = len(decoded.bytes)
    #last_byte = -1
    for i in decoded.bytes:
        # 255 for ff
        # 165 for a5
        # 90 for 5a
        if i == 0 and ((count < 0x1970) or (count > 0xa532f)):# or i == 90:# and count < 0x1c00:#((count > 0xce and count < 0xef8) or ( count > 0xf4b and count < 0x1028) or (count > 0x104b and count < 0x13d0)): #165
            count = count+0x1
            continue
        
        count = count + 0x1
        
        if(count % 0x1EFF0 == 0):
            progress.print(int( (count / length) * 100))
        
        
        #if last_byte == i and ((count <  0x13d0) or (count > 0xa532f)):
         #   continue

        #last_byte = i
        

        output.append(BitArray(uint=i, length=8))
        

    progress.print(100)
    return output

def new_remove_buffer(decoded):
    progress = Progress("Removing Buffer")
    output = BitArray()
    count = 0x0
    length = len(decoded.bytes)
    last_byte = [256, 256, 256]
    for i in decoded.bytes:

        if last_byte[0] == i:
            check=True
        else:
            check=False
        last_byte[2] = last_byte[1]
        last_byte[1] = last_byte[0]
        last_byte[0] = i
        count+=1

        if check:
            continue

        if (last_byte[2] + last_byte[1] == last_byte[0] + i):
            check=True
        else:
            check=False

        if check:
            continue
        output.append(BitArray(uint=last_byte[0], length=8))
        if(count % 0x1E00 == 0):
            progress.print(int( (count / length) * 100))
    progress.print(100)
    return output


# Helper function to ask user if this is what they want
def check_user(data=None) -> bool:
    if data != None:
        dumphex(data)
    #os.system("vlc --show-hiddenfiles --play-and-exit video_file.vid")
    answer = input("Press y to end: ")
    if answer == 'y':
        return True
    return False


# Checks error and automatically stops and grabs array if so
def check_error(H, filename):

    os.system("ffmpeg -v error -i " + filename + " -f null - 2> error.log")

    lines = []
    with open("error.log", 'r') as f:
        lines = f.readlines()

    # Should let me sleep while this works away
    if len(lines) == 0:
        with open("Possible.hamming", 'a+') as f:
            f.writelines(np.array2string(H))
            print("Possible")
    else:
        print("Bad")

        



# This will be a program to iterate through different versions of hamming code.
# From which is will ask the user if the heading looks about right. this should
# automate the frustration of testing hamming codes.
def auto_change(r=3, m=4,rAtEnd=True, ham=hamm.fec_hamming, filename="decoded.ham", output="video_file.vid"):
    # Create base hamming matrix
    #ham = hamm.fec_hamming(r)
    #ham = rev_ham(r)
    #ham = Hamming_84()

    # Better hamming which can dynamically call any of the hamming classes
    ham = ham(r)
    H = ham.H
    #H = ham_74_rev

    #print(f"Starting auto check with r={r} m={m}:\n")
    for i in permutate_ham(r+m,m,rAtEnd):
        print('\n')
        # Create random H from here
        ham.H = H[:,i]
        #print(ham.H)

        try:
            #progress_bar("decoding",0)
            #bits = legacy_decode_from_file("decoded.ham")
            bits = decode_from_file("decoded.ham",ham)
            #progress_bar("decoding",90)
            bits = bits[:len(bits)-(len(bits)%8)]
            #bits = new_remove_buffer(bits)
            bits = remove_buffer(bits)
            #bits = new_buffer(bits)
            bits.tofile(open("video_file.vid",'wb'))
            #progress_bar("decoded",100)
        except (KeyError, HammingError):
            #print("decoding{:.>61}".format("error"))
            continue

        with open(output, 'rb') as f:
            dumphex(f.read(16*20))
            #check_user(f.read(16*20))
        # Run video wait 1 second, continue
        #os.system("vlc --show-hiddenfiles --play-and-exit -q --no-qt-error-dialogs --avcodec-error-resilience=2 video_file.vid")
        #sleep(1)

        check(output)
        #check_error(ham.H,output)

        print("past\n")
        print(ham.H,'End\n')
        # Ask user if the above is correct and whether the program should halt
        #with open(output, 'rb') as f:
            #data = f.read(16 * 40)
            #if check_user():
                # Print the hamming code to ensure the user gets it
                #print("This is the ham matrix\n",ham.H)

                #return

    print(" Failed to find one")

# This will be a program to iterate through different versions of hamming code.
# From which is will ask the user if the heading looks about right. this should
# automate the frustration of testing hamming codes.
def auto_change_buffer(r=3, m=4,rAtEnd=True, ham=hamm.fec_hamming, filename="decoded.ham", output="video_file.vid"):
    # Create base hamming matrix
    #ham = hamm.fec_hamming(r)
    #ham = rev_ham(r)
    #ham = Hamming_84()

    # Better hamming which can dynamically call any of the hamming classes
    ham = ham(r)
    H = ham.H
    #H = ham_74_rev

    #print(f"Starting auto check with r={r} m={m}:\n")
    for i in permutate_ham(r+m,m,rAtEnd):
        print('\n')
        # Create random H from here
        ham.H = H[:,i]
        #print(ham.H)

        try:
            #progress_bar("decoding",0)
            #bits = legacy_decode_from_file("decoded.ham")
            bits = decode_from_file("decoded.ham",ham)
            #progress_bar("decoding",90)
            #bits = new_remove_buffer(bits)
            #bits = remove_buffer(bits[:len(bits)-(len(bits)%8)])
            bits = bits[:len(bits) - (len(bits) % 8)]
            bits.tofile(open("video_file.vid",'wb'))
            #progress_bar("decoded",100)
        except (KeyError, HammingError):
            #print("decoding{:.>61}".format("error"))
            continue

        with open(output, 'rb') as f:
            dumphex(f.read(16*20))
        #os.system("vlc --show-hiddenfiles --no-audio --play-and-exit -q --no-qt-error-dialogs --avcodec-error-resilience=2 video_file.vid")
        #sleep(1)
        check(output)
        #check_error(ham.H,output)

        # Ask user if the above is correct and whether the program should halt
        #with open(output, 'rb') as f:
            #data = f.read(16 * 40)
            #if check_user():
                # Print the hamming code to ensure the user gets it
                #print("This is the ham matrix\n",ham.H)

                #return

    print(" Failed to find one")


# Go after matrix, increasing its size over time and going to the point where it is using padding to make it work
def auto_final(filename="decoded.ham", output='video_file.vid'):


    #binary = BitArray(filename=filename)

    for j in range(4, 9):
        # make new ham object
        ham = hamm.fec_hamming(j)

        #auto_change_buffer(r=j, m=ham.n-j )
        #auto_change(r=j, m=ham.n-j )
        #auto_change(j, ham.n-j, False, rev_ham)

        #auto_change_buffer(j, ham.n-j, False, rev_ham)
        auto_change_buffer(r=j, m=ham.n-j )
        #print(ham.H)
        #code = np.array(list(map(lambda x: ord(x) - 48, list(binary.bin + '0' * (ham.n - len(binary.bin) % ham.n)))))
        """
        decoded = decode_from_file(filename,ham)

        decoded = remove_buffer(decoded[:len(decoded)-(len(decoded)%8)])

        decoded.tofile(open(output, 'wb'))

        with open(output, 'rb') as f:
            data = f.read(16*30)
            if check_user(data):
                break
            """








def main():
    #bits = legacy_decode_from_file("decoded.ham")
    #ham = hamm.fec_hamming(3)
    ham = rev_ham(3)
    ham.H=ham_74_reg_rev
    #ham.H = ham_74
    bits = decode_from_file("decoded.ham", ham=ham)
    #bits = remove_buffer(bits[:len(bits)-(len(bits)%8)])
    bits.tofile(open("video_file.vid",'wb'))

    # H[7,4] with parity at the beginning
    #auto_change(3,4,False,rev_ham)

    # H[7,4] with parity at the end
    #auto_change(3,4)

    # H[8,4] with parity at the end
    #auto_change(4,4,ham=Hamming_84)

    # H[8,4] with parity at the beginning
    #auto_change(4,4,False,ham=rev_ham_84)

    #auto_final()

if __name__ == "__main__":
    main()
