import os, sys
# Import Signal Handler to handle SIGPIPE 
from signal import signal, SIGPIPE, SIG_DFL


# Fifo path
file_path = "/tmp/gps_fifo"


def generator():
    while True:
        for line in open("./support/fake_gps.log", 'r'):
            yield line
    
# What will actually write to the fifos
def fifo_write():

    try:
        os.mkfifo(file_path)
    except OSError as e:
        print("Failed to create FIFO: %s" % e)
    else:
        # Accesss file
        for line in generator():
                # Doing this as such ensures that the pipe is not broken 
                try:
                    fifo = open(file_path, 'w')
                    for i in line:
                        fifo.write(i)
                    fifo.close()
                except IOError:
                    pass

# Cleanup script
def fifo_close():
    try:
        os.remove(file_path)
    except OSError as e:
        print("File removed")

import atexit

if __name__ == "__main__":
    atexit.register(fifo_close)
    fifo_write()
