import os, struct, sys
from Crypto.Cipher import AES
import codecs

# Create objects which will store the values for key and iv
key = 'GNG$GNG$GNG$GNG$'.encode("utf-8")
iv = 'GNG$GNG$GNG$GNG$'.encode("utf-8")
File = "./Logs/20200628_153027.log"

# Define a function which will loop through possible values
# key defined as four repeats of the lat, the iv is 3 of long + '0'
def crack_this_shit():
    count = 0
    # First will set up a loop through all possible values of the lat and long
    for lat in range(1500, 8060):
        for lon in range(1500, 16060):
            key = (str(lat))
            key = ( ( key.ljust(4,'0') )[::-1] * 4).encode()
            iv = str(lon)
            iv = (( ( iv.rjust(5,'0') )[::-1] * 3 ) + '0').encode()
            
            # Decrypt file then check for errors and repeat
            Decrypt_File(File)
            Check_Type(File)
            count += 1
            if count % 3521 == 0:
                print("Key = ", key)
                print("IV =  ", iv)
                cout = 0

# Function will check the file for errors
def Check_Type(File):
    try:
        f = codecs.open(File + ".txt", encoding='utf-8', errors='strict')
        for _ in f:
            pass
        print("CORRECT KEY AND IV")
        print("KEY: ", key.decode())
        print("IV:  ", iv.decode())
        # If it made it through the file then terminate the program
        sys.exit()
    except UnicodeDecodeError:
        return

# Define Function to decrypt log files
def Decrypt_File(in_filename):
    """
    This will be taking the first 32 bytes of the file to get the key and IV
    values which are used on the rest of the file to decrypt it. Following this
    it should output a viable file of text
    """
    
    # Create the outfile name
    outfile = in_filename + ".txt"
    
    # Chunksize
    chunksize = 16
    
    # Read Binary data from file
    with open(in_filename, 'rb') as ifile:
        
        # Create AES decryptor from key and IV values
        decryptor = AES.new(key, AES.MODE_CBC, iv)
        
        # Stream ifile directly into outfile
        with open(outfile, 'wb') as ofile:
            while True:
                chunk = ifile.read(chunksize)
                # Check EOF or modify chunksize for AES padding
                if len(chunk) == 0:
                    break
                ofile.write(decryptor.decrypt(chunk))


if __name__ == "__main__":      
    crack_this_shit()
    
