"""
Purpose:

This program is built to be able to remove the buffer which has been added
onto the output file. This will be done by checking the output stream. In the
output stream it will check for a long stream of bits which are the same.

In doing so this should allow for it to remove the padding without removing 
the useful bits.
-------------------------------------------------------------------------------
How:
This will be done by having two buffers, one of which will be the input list. 
This list will gather hex data and test for repetition, the repetition can be 
less than 30 bytes long, if no repetition it just moves said list into the
regular storage. 

If it finds repetition it will continue looking for said pattern and delete all of
it. It will then repeat. This can also accept arguments of byte patterns which can 
make it a bit more accurate, potentially.
-------------------------------------------------------------------------------
TODO:
- Add functions to enable for checking patterns of repeating bytes
- System to check for certain byte paterns, potentially some regex?
- Buffer which handles these checks
- Buffer which handles the file stuff to get in a file and output the file without the padding
"""

"""
This class is the padding buffer, which is responsible for handling data. Given
by the other buffer, as it does this it will return data 
"""
class Padding_Buffer():

    """
    Within init, define a numbr 
    """
    def __init__(self, )