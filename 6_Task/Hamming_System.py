import numpy as np
from bitstring import BitArray
import utils

"""
This is a list of generator polynomials which can be drawn from to
make the hamming codes.
"""
polynomials = {
     3: np.array([1,1]),
     7: np.array([1,0,1,1]),
    15: np.array([1,0,0,1,1]),
    31: np.array([1,0,0,1,0,1]),
    63: np.array([1,0,0,0,0,1,1]),
   127: np.array([1,0,0,0,0,0,1,1]),
   255: np.array([1,0,0,0,1,1,0,1,1])
}

class GaloisFieldError(Exception):
    pass        

class HammingDoubleBitError(Exception):
    pass

"""
This class will be the hamming code generation class. It
will generate based on a given block size length. either
of the exact type, or a shortened version.

This is loosely based off the hamming class defined in:
https://github.com/mwickert/scikit-dsp-comm/blob/master/sk_dsp_comm/fec_block.py

This is changed to use a Galois Field as a generator of standard hamming codes

"""
class Hamming():
    def __init__(self, block_size, polynomial=None, shortened_code=False, parityAtFront=False, extraParity=False, progressBar=False, clearonError=True):
        self._shortened_code = shortened_code
        self._parityAtFront = parityAtFront
        self._extraParity = extraParity
        self._block_size = block_size
        self.clear = clearonError

        # define decded bits as None
        self.decoded_bits = None
        
        # Progress Bar will decide if a progress bar is outputed
        self.progress = progressBar
        parity = 2
        while True:
            # increase r until the block_size is < the size from r
            if 2**parity - 1 >= block_size:
                break
            parity += 1
        block_size = 2**parity-1

        self.G, self.H, self.R, self.message_length, self.parity_length = self.__generate_hamming__(block_size, polynomial)

        # If parity is not at end then reverse 
        if self._parityAtFront:
            # Compute full sized block size for the code to use
            block_size = 2**self.parity_length - 1
            # flip G around
            temp = np.zeros((self.message_length, self.message_length))
            temp[:,:] = self.G[:, :self.message_length]
            self.G[:,:self.parity_length] = np.zeros((self.message_length,self.parity_length))
            self.G[:,:self.parity_length] = self.G[:,self.message_length:]
            self.G[:,self.parity_length:] = np.zeros((self.message_length, self.message_length))
            self.G[:,self.parity_length:] = temp

            # Flip H around
            temp = np.zeros((self.parity_length, self.message_length))
            temp[:,:] = self.H[:, :self.message_length]
            self.H[:, :self.parity_length] = np.zeros((self.parity_length,self.parity_length))
            self.H[:,:self.parity_length] = self.H[:,self.message_length:]
            self.H[:,self.parity_length:] = np.zeros((self.parity_length, self.message_length))
            self.H[:,self.parity_length:] = temp

            # Flip R around
            for i in range(self.message_length):
                self.R[i,:] = np.roll(self.R[i,:], self.parity_length)
            #R = np.zeros((self.message_length, block_size), dtype=int)
            #R[:,self.parity_length:] = np.diag([1 for _ in range(self.message_length)])

            if block_size > self._block_size:
                self.message_length = self._block_size - self.parity_length
                # Now shorten the hamming code
                self.R = np.array(self.R[:, :self._block_size])
                self.R = np.array(self.R[:self.message_length,:])

                # Reduce H
                self.H = np.array(self.H[:,:self._block_size])

                # Reduce G
                self.G = np.array(self.G[:, :self._block_size])
                self.G = np.array(self.G[:self.message_length,:])
            
            # If wanting an extra parity bit then create an extended version
            if self._extraParity:
                self.parity_length += 1
                self._block_size += 1
                G = np.zeros((self.message_length, self._block_size), dtype=int)
                H = np.zeros((self.parity_length,self._block_size), dtype=int)
                P = np.zeros((self.message_length, self.parity_length), dtype=int)
                R = np.zeros((self.message_length, self._block_size), dtype=int)

                # Now move the regs into it
                # Set up G
                G[:,self.parity_length:] = self.G[:,self.parity_length-1:]
                G[:,:self.parity_length-1] = self.G[:,:self.parity_length-1]
                G[:,self.parity_length-1] = np.ones(self.message_length)
                self.G = np.array(G, dtype=int)

                # Set up H
                #H[]


        else:        
            # If the block_size is less then the official sizes then convert to shortened
            # hamming code
            if self._block_size < 2**self.parity_length - 1:

                self.message_length = self._block_size - self.parity_length
                
                full = 2**self.parity_length - 1
                # create a reduced R
                self.R = np.array(self.R[:, full-self._block_size:])
                self.R = np.array(self.R[full-self._block_size:,:])

                # Reduce H
                self.H = np.array(self.H[:,full-self._block_size:])

                # Reduce G
                self.G = np.array(self.G[:, full-self._block_size:])
                self.G = np.array(self.G[full-self._block_size:, :])

        # Finally generate the syndrome dictionary which is used for quick error detection
        self._syn_ = {0:-1}
        for i in range(self.H.shape[1]):
            self._syn_[Hamming.bintoint(self.H[:,i].T)] = i

    def __generate_hamming__(self, block_size, polynomial=None):

        if block_size < 3:
            raise ValueError("block size is too small to be a hamming code")
        # Currently the program cannot go larger than the block size of 255
        if block_size > 255 and not self._extraParity and polynomial != None:
            raise NotImplementedError("Block Size is too large for this program now")
        # First create the hamming code parity size, and message size
        parity = 2
        while True:
            # increase r until the block_size is < the size from r
            if 2**parity - 1 >= block_size:
                break
            parity += 1

        # Get the generator polynomial
        # if no custom polynomial use the defualt, otherwise sanity check that polynomial is of correct degree
        if polynomial != None:
            assert len(polynomial) >= parity
            m = np.array(polynomial, dtype=int)
        else:
            m = polynomials[2**parity-1]
        
        self.poly = m
        message_length = 2**parity - parity - 1
        g = np.zeros(block_size)

        # Generate Matrices which are to be used
        G = np.zeros((message_length,block_size), dtype=int)
        H = np.zeros((parity,block_size), dtype=int)
        P = np.zeros((message_length, parity), dtype=int)
        R = np.zeros((message_length, block_size), dtype=int)

        # Create the generator polynomial
        g[:m.size] = m

        # Roll the polynomial and find the rref, as well as making an 
        # augmented identity matrix 
        
        # Generate the matrix
        for i in range(message_length):
            G[i,:] = np.roll(g,i)
        
        # Compute RREF
        #utils.ToReducedRowEchelonForm(G)
        #G = Hamming.np_bin(G)
        
        # Compute right side identity matrix
        for i in range(G.shape[0]):
            for j in range(i):
                if G[j,i]:
                    G[j,:] = Hamming.np_bin(G[j,:] + G[i,:])
    
        # Take P from G parity matrix side
        P = G[:,message_length:]

        # The transpose of P will be the left side of H
        H[:, :message_length] = P.T
        # Create identity matrix which will be on the right side of H
        H[:, message_length:] = np.diag([1 for _ in range(parity)])

        # Generate R
        R[:, :message_length] = np.diag([1 for _ in range(message_length)])

        # Check if wanting an extra parity bit, if so modify code
        if self._extraParity:
            parity += 1
            self._block_size += 1
            block_size += 1

            # Expand H into a list and modify to fit extra parity
            temp = np.zeros((parity, block_size), dtype=int)
            temp[:parity-1,:message_length] = H[:,:message_length]
            temp[:parity-1,message_length:message_length+parity-1] = H[:,message_length:]



        # Return G, H, R, message_length, parity
        return G, H, R, message_length, parity

    def encode(self, message):
        """
        Encodes input bits to hamming code
        """
        if message.dtype != np.dtype(int):
            message = message.astype(int)
            #raise ValueError("Message must be of numpy dtype int")

        if message.size % self.message_length != 0 or message.size < self.message_length:
            raise ValueError("Invalid Message Length, must be multiple of {}".format(self.message_length))

        # Number of blocks there are
        n_blocks = int(message.size/self.message_length)

        # Create buffer for codeword output
        codewords = np.zeros(n_blocks*self._block_size, dtype=int)

        # Reshape message input to align with G
        message = np.reshape(message,(1,message.size))

        # Convert message bits to hamming encoded bits
        for i in range(1,n_blocks+1):
            codewords[(i-1)*self._block_size:i*self._block_size] = \
                Hamming.np_bin(np.matmul(message[(i-1)*self.message_length:i*self.message_length], self.G))
        
        return codewords

    def decode(self,codewords: np.array):
        """
        Method takes codewords of the multiple of the block size

        From this it is able to decode it and correct error bits, this taken
        from a syndrome dictionary of the possible error values

        The output will be the decoded message, this can also be digested into a
        file and will be saved to the class for future use.
        """
        # Assertions for input sanitization
        if codewords.ndim != 1:
            raise ValueError("Codewords must be a 1 dimensional array")
        if codewords.dtype == np.dtype(int) != int:
            codewords = codewords.astype(int)
            #raise ValueError("Codewords must be an array of ints")
        if codewords.shape[0] % self._block_size or codewords.shape[0] < self._block_size:
            raise ValueError("Codewords is not a multiple of the block size {}".format(self._block_size))

        # Compute Number of blocks in codewords
        n_blocks = int(len(codewords)/self._block_size)

        # Progress bar, decided by user inputing if they wish it to display
        progress = utils.Progress("Decode Hamming Code", buffer=n_blocks, step=int(n_blocks/12),enabled=self.progress,clearonError=self.clear)

        # Create buffer for decoded bitarray
        self.decoded_bits = np.zeros(n_blocks * self.message_length, dtype=int)

#        codewords = np.reshape(codewords,(1,codewords.size))
        for i in range(1,n_blocks+1):

            # Check progress
            progress.print(i)

            # Create Syndrome of the codeword
            S = Hamming.np_bin(np.matmul(self.H, codewords[(i-1)*self._block_size:i*self._block_size].T))

            error_pos = -1

            # Use sum of the syndrome to search the dictionary, if key error then return Hamming error 
            # That there is a double bit error
            try:
                error_pos = self._syn_[Hamming.bintoint(S.T)]
            except KeyError:
                raise HammingDoubleBitError("Double Bit Encountered")

            # Replace the error
            if error_pos != -1:
                codewords[(i-1)*self._block_size + error_pos] = (codewords[(i-1)*self._block_size + error_pos]+1) %2

            # Use R to decoded to messages and then add to decoded
            self.decoded_bits[(i-1)*self.message_length:i*self.message_length] = \
                np.matmul(self.R,codewords[(i-1)*self._block_size:i*self._block_size].T).T 
        
        # Return decoded bits, copied to a new np.array to keep continuity
        del(progress)
        return np.array(self.decoded_bits)

    # Function will digest decoded bits to file given by the filename
    def digest(self, filename: str):
        if not np.any(self.decoded_bits):
            raise RuntimeError("No bits have been decoded to digest to a file")
        # convert binarray to a bitstring
        f = lambda x: chr(x+48)
        binary = BitArray(bin=''.join(list(map(f,self.decoded_bits.tolist()))))
        binary.tofile(open(filename, 'wb'))
    # Helper function to make np bin array into int
    @staticmethod
    def bintoint(bits):
        m = bits.shape
        a = 2**np.arange(m[0],dtype=int)
        return np.sum(np.matmul(a,bits))
    # Helper function to make np_array binary
    @staticmethod
    def np_bin(arr):
        f = lambda x: x%2
        return f(arr)

# Import algorithms to implement factoring
from sympy.polys.galoistools import gf_from_dict, gf_berlekamp
# Import field operators
from sympy.polys.domains import ZZ

class Hamming_Codes():
    """
    Will return a iterator of codes and can use a generator which returns a series of these
    """
    def __init__(self, block_size, check_reversed=True):
        # save block_size, and get R
        self.block_size = block_size
        self.check_reversed = check_reversed
        self.r = 2
        while True:
            if 2**self.r - 1 >= block_size:
                break
            self.r += 1

        #assert(self.r < 13)

    def __iter__(self):
        poly_gen = gf_from_dict({(2**self.r - 1): ZZ(1), 0:ZZ(1)}, 2, ZZ)

        # Generate factors of the polynomial
        factored = gf_berlekamp(poly_gen, 2, ZZ)

        # Get polynomials of parity r
        self.gen_polynomial = [i for i in factored if len(i) >= self.r]

        if self.check_reversed:
            self.rev_polynomial = [i for i in self.gen_polynomial]
        return self

    def __next__(self):

        if len(self.gen_polynomial)==0:
            raise StopIteration()

        if self.check_reversed:
            if len(self.rev_polynomial):
                return Hamming(self.block_size, polynomial=self.rev_polynomial.pop(), parityAtFront=True, progressBar=True), True
        
        return Hamming(self.block_size, polynomial=self.gen_polynomial.pop(0), progressBar=True), False



def main():
    ham = Hamming(7)
    print(ham.H)
    h = ham.encode(np.array([1,0,1,1],dtype=int))
    print(h)
    print(ham.decode(h))

if __name__ == "__main__":
    main()