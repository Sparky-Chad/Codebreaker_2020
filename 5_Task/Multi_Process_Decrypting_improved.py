
# Importing the needed AES things
from Crypto.Cipher import AES
# Importing shared memory stuffs
from multiprocessing import Pool, cpu_count
# Import collectios deque
from collections import deque
from time import sleep
import codecs


NUM_PROCESSES= 9

file_bytes=[]
#file_name="./Logs/20200628_153027.log"
files = ["./Logs/20200628_153027.log", "./Logs/20200630_161219.log", "./Logs/20200723_183021.log", "./Logs/20200920_154004.log"]



class EarlyExit(Exception):
    def __init__(self, key, iv, plainstring):
        Exception.__init__(self)
        self.key = key
        self.iv = iv
        self.plainstring = plainstring

class generator:
    def __init__(self, patch, reverse=True):
        self.lat = patch[0]
        self.lon = patch[1]
        self.length = patch[2]
        self.counter = 0
        self.reverse = reverse

    def __iter__(self):
        self.counter = 0
        return self
    
    # Static generator yields a number of iterations of lat_long coordinate strings
    def __next__(self):
        if(self.counter >= self.length or self.lon > 18060):
            raise StopIteration()
        #assert (patch is tuple and len(patch) == 3)
        key = ( str(self.lat) ).ljust(4, '0')
        iv  = (( str(self.lon + self.counter) ).ljust(4, '0')).rjust(5, '0')
        
        self.counter += 1
        
        if self.reverse:
            return ((key[::-1] * 4).encode(), ( (iv[::-1] * 3) + '0').encode())
        else:
            return ((key * 4).encode(), ( (iv * 3) + '0').encode())
            

def child_process(patch):
    #file_bytes = chunk_read(file_name)
    
    print("->", patch)
    key, iv, plaintext = None, None, None
    #mybytes = bytearray()
    for key, iv in generator(patch):
        plaintext=[]
        #mybytes = bytearray()
        decryptor = AES.new(key, AES.MODE_CBC, iv)
        
        # Now iterate through each object in the memory
        # By checking the encoding first we can more quickly move through the files
        try:
            #for chunk in file_bytes:
            with open(file_name, 'rb') as file_bytes:
                #mybytes.extend(decryptor.decrypt(chunk))
                plaintext.append( codecs.decode( decryptor.decrypt(file_bytes.read(16)) ) )
        
        # If part of the file is not readable just don't read it
        except UnicodeError:
            continue
        
        # If we have found the proper stuff raise exception and do output
        return (key.decode(), iv.decode(), plaintext)
    
    
    
# Class which will simply create an iterator through different coordinate values and return it for another function to be able to handle it

# Each instance will also be told to run for a certain number of iterations that 
# the iterator can hopefully keep track of to ensure that there is not too much 
# waste of processor time

# I think 1000 iterations should work just fine
class Coordinate:
    def __init__(self, lat_ends = [0, 9060], lon_ends = [0, 18060], reverse=False, \
                      iterations=18061):
        self._lat_ends=lat_ends
        self._lon_ends=lon_ends
        self.reverse = reverse
        self.iterations = iterations
        
        
    def __iter__(self):
        return self.generator()
    
    def generator(self):
        for lat in range(self._lat_ends[0], self._lat_ends[1]+1):
            for lon in range(self._lon_ends[0], self._lon_ends[1]+1, self.iterations):
                yield [lat, lon, self.iterations]
       
        
"""
Class which handles queueing children for the process to run crackers
"""        
class Dispatcher:
    def __init__(self, pool):
        self.pool = pool
        self.q = deque()
        

    def queue_work(self, *args):
        while len(self.q) > NUM_PROCESSES * 3:
            # provided the workers have significant work to do,
            # it will "take a long time" to finish the work
            # already queued.  Rather than swamp the mp machinery
            # with even more pending tasks, wait for some to
            # finish first.
            self.unqueue()
        self.q.append(self.pool.apply_async(child_process, args))
        

    def unqueue(self):
        if self.q:
            # note:  the main program spends most of its time
            # blocked on the .get(); that's because it can
            # generate prefixes far faster than workers can
            # process them
            result = self.q.popleft().get()
            print(".")
            if result is not None:
                print(f"Key: {result[0]}\nIV: {result[1]}")
                raise EarlyExit(result[0], result[1], result[2])
                
    def drain(self):
        while self.q:
            self.unqueue()
    
    
# Returns binary file data split into 16 byte chunks
def chunk_read(filename, chunks=16) -> list:
    file_bytes = []
    with open(filename, 'rb') as ifile:
        while True:
            chunk = ifile.read(16)
            if len(chunk) == 0:
                break
            file_bytes.append(chunk)
            
    return file_bytes
    
"""
    Defines the main controller functions, this will simply create a coordinate
    object and continue calling new objects which will run AES decryption on 
    the file buffer it is sharing to them all.
"""
def parent_worker(dispatcher):
    global file_bytes
    global file_name# = "./Logs/20200628_153027.log"

    coords = Coordinate()
    file_bytes = chunk_read(file_name)
    
    print("Begin Creation of pool")
    for i in coords:
        dispatcher.queue_work(i)
    
    coords = Coordinate(reverse=False)
    for i in coords:
        dispatcher.queue_work(i)
    
    # When complete finish rest of tasks
    dispatcher.drain()
    
    # Destroy shared memory
    #cipher_file.unlink()
    
    
if __name__ == "__main__":
    global file_name
    for i in files:
        file_name = i
        pool = Pool(NUM_PROCESSES)
        dispatch = Dispatcher(pool)
        
        try:
            parent_worker(dispatch)
        except EarlyExit as e:
            with open(f"{file_name}_decrypted.log", 'w') as ofile:
                ofile.writelines(e.plainstring)
            with open("./Logs/key_file", 'a') as ofile:
                ofile.write(f'\nKey: {e.key}\nIV: {e.iv}')
            print("Completed\nKey: ", e.key, '\nIV:  ', e.iv)

            sleep(2)
        else:
            print("This has failed...")
            sleep(2)
        
        pool.close()
        pool.terminate()
        pool.join()
    
    
    
