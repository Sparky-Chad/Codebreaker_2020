from string import ascii_letters, digits, punctuation
from random import sample
from math import factorial, ceil
import numpy as np
import os
import sys

def bufferToHex(buffer, start, count):
    accumulator = ''
    for item in range(count):
        accumulator += '%02x' % buffer[start + item] + ' '
    return accumulator

def bufferToAscii(buffer, start, count):
    accumulator = ''
    for item in range(count):
        char = chr(buffer[start+item])
        if char in ascii_letters or \
           char in digits or \
           char in punctuation or \
           char == ' ':
            accumulator += char
        else:
            accumulator += '.'
    return accumulator

def dumphex(buffer, linesize=16):
    size = len(buffer)
    print()
    i = 0
    while i < size:
        hexi = bufferToHex(buffer, i, linesize)
        ascii = bufferToAscii(buffer, i, linesize)

        print(hexi, end='')
        print('|',ascii,'|')

        i += linesize

        if size - i< linesize:
            linesize = size - i

class Progress:

    # Disablled progress class all functions return
    class Disabled():
        def __init__(self):
            return

        def print(self, *args):
            return
        def error(self, *args):
            return
        def __reset_out__(self, *args):
            return
        def __set_print__(self, *args):
            return
        def __print_replace__(self, *args):
            return
    # Inner class to replace 
    class writter_wrapper():
        # Creates wrapper which can count how many lines from the progress bar
        def __init__(self):
            self.count=0

        def write(self, text):
            sys.stdout = sys.__stdout__
            #log = False
            if self.count == 0:
                sys.stdout.write(u'\u001b[3B' + '\nLog:\n')
                self.count += 2
            else:
                # move down past progress bar Then move for number of lines already
                sys.stdout.write(u'\u001b[3B' + u'\u001b[{}B'.format(self.count))

            # write text
            sys.stdout.write(text)
            

            # Count number of newlines in text
            self.count += len([i for i in text if i == '\n'])

            
            # Return to start of buffer
            sys.stdout.write(u'\u001b[{}A'.format(self.count) + u'\u001b[3A' + u'\u001b[1000D')

            #if log:
               # sys.stdout.write(u'\u001b[1A')
               # self.count += 1 
            
            sys.stdout.flush()
            sys.stdout = self
            # return to sender
        
        def flush(self):
            sys.stdout = sys.__stdout__
            sys.stdout.flush()
        
        def clear(self):
            # clear all lines and return
            #tput = subprocess.Popen(['tput','cols'])
            #cols = int(tput.communicate()[0].strip())
            cols = 60#int(os.popen('stty size', 'r').read().split()[0])
            sys.stdout = sys.__stdout__
            for _ in range(self.count + 3):
                sys.stdout.write(''.join([' ']*cols)+'\n')
                #sys.stdout.write('\033[F\n')
                sys.stdout.flush()

            # Return back to start
            sys.stdout.write(u'\u001b[{}A'.format(4+self.count))
        def __del__(self):
            self.flush()
            sys.stdout = sys.__stdout__
            sys.stdout.write(u'\u001b[{}B'.format(self.count))

    # Added option to disable the progress bar
    def __init__(self, label="Progress", buffer=None, step=None, enabled=True, clearonError=False):
        """
        Creates the progress bar

        Parameters
        label: text displayed above the progress bar for ease of interpreting it

        buffer: either the buffer, or the length of the buffer to auto compute progress
        
        step: defines how many steps between computing the progress bar should be completed
        
        enabled: defines if the progress bar is enabled, if False casts to disabled progress bar
        object so methods will just return rather then needing more help 

        clearonError: Changes error method to clear the progress bar if an error is encountered
        """

        # If disabled return a print object which has no functionality
        if not enabled:
            self.__class__ = Progress.Disabled
            return
        self.buffer = None

        self.clearonError = clearonError
        # Set buffer
        if not buffer is None:
            if isinstance(buffer, int):
                self.buffer=buffer
            elif hasattr(buffer, '__len__'):
                self.buffer = len(buffer)
            else:
                raise ValueError("buffer must be iterable or int")
        else:
            self.buffer = None

        # Set step
        if step is None or step == 0:
            self.step = None
        else:
            assert isinstance(step, int)
            self.step = step

        # Variable for telling if 100 had been hit before
        self.done = False

        self.label = label
        print(self.label, '\n\n')
        sys.stdout.write(u'\u001b[1000D')
        sys.stdout.write(u'\u001b[3A')
        self.__print_replace__()
        self.print(0)

    def print(self, percent=0):

        # Reset out so this class doesn't worry
        self.__reset_out__()

        if not (self.buffer is None):
            # Check if step is defined, if so check if this is fulfilled
            if not self.step is None:
                if percent % self.step:
                    return
            percent = ceil( (percent / self.buffer) * 100 )
        
        if percent > 100:
            raise ValueError("Percent is too high")

        if self.done:
            return

        print(self.label,'\n')
        width = int(percent/2)
        print('[' + '#' * width + '.' * (50-width) + '] ' + '{:>2}%'.format(percent))
        sys.stdout.write(u'\u001b[1000D')
        sys.stdout.write(u'\u001b[3A')
        if percent == 100:
            print("\n")
            sys.stdout.write(u'\u001b[53CComplete')
            print("\n")
            self.done = True

        sys.stdout.flush()
        # Set out again
        if not self.done:
            self.__set_print__()

    # Print that error has occured
    def error(self):
        if self.done:
            return
        self.__reset_out__()
        if self.clearonError:

            # clear output
            self.wrapper.clear()

        else:
            print(self.label, '\n')
            print('[' + '%' * 50 + '] ' + 'Error')
            self.done = True

    def __del__(self):
        self.buffer = None
        if not self.done:
            self.error()
        self.__reset_out__()
        del(self.wrapper)
    # Class creates its own method of handling stdout
    def __reset_out__(self):
        sys.stdout = sys.__stdout__

    def __set_print__(self):
        try:
            sys.stdout = self.wrapper
        except AttributeError:
            pass
    
    def __print_replace__(self):
        self.wrapper = self.writter_wrapper()
        sys.stdout = self.wrapper

def progress_bar(first, percent):
    print(first,':\n\n')
    sys.stdout.write(u'\u001b[2A')
    width = percent - 20
    print('[' + '#' * width + ' ' * (80-width) + '] ' + '{}'.format(percent))


class permutate_ham:
    def __init__(self, total=7, m=4, rAtEnd=True):
        self.r = total - m
        self.m = m
        self.rAtEnd = rAtEnd
        # This is the first permutation to return the same matrix from r and m
        # create two which can then be added together
        if self.rAtEnd:
            self.r_matrix = list(range(self.m, self.r+self.m))
            self.scramble = list(range(self.m))
        else:
            self.r_matrix = list(range(self.r))
            self.scramble = list(range(self.r,self.m+self.r))
        # Get total and previous which act as end states for the iterator
        self.total = factorial(self.m)
        self.previous = []


    # This will permutate posibilities of data which can then be used for changing
    # what the later matrix will be.

    def __iter__(self):
            return self


    def __next__(self):

        if len(self.previous) == 0:
            out = list(range(self.m+self.r))
            self.previous.append(out)
            return out
        # Return scrambled list only if it doesn't already exist
        if len(self.previous) == self.total:
            raise StopIteration
        if self.rAtEnd:
            scrambled = []
            while scrambled in self.previous or len(scrambled)==0:
                scrambled = sample(self.scramble,k=self.m) + self.r_matrix
            self.previous.append(scrambled)
            return scrambled
        else:
            scrambled = []
            while scrambled in self.previous or len(scrambled)==0:
                scrambled = self.r_matrix + sample(self.scramble,k=self.m)
            self.previous.append(scrambled)
            return scrambled

# binary which can format depending on some specifications of a list of ints or char string, or list of chars.
# The basic will format it as a string, without the b, then it will change it to other formats if the user would like
def binary(num, length=8, outputList=False, outputAsInt=True):
    output = format(num, '0{}b'.format(length))

    if outputList:
        output = list(output)
        if outputAsInt:
            output = list(map(lambda x: int(x) - 48, output))

    # Return output as determined by function
    return output


def ToReducedRowEchelonForm( M, lead=0):
    if M is None: return
    rowCount = len(M)
    columnCount = len(M[0])
    for r in range(rowCount):
        if lead >= columnCount:
            return
        i = r
        while M[i][lead] == 0:
            i += 1
            if i == rowCount:
                i = r
                lead += 1
                if columnCount == lead:
                    return
        M[i],M[r] = M[r],M[i]
        lv = M[r][lead]
        M[r] = [ mrx / float(lv) for mrx in M[r]]
        for i in range(rowCount):
            if i != r:
                lv = M[i][lead]
                M[i] = [ iv - lv*rv for rv,iv in zip(M[r],M[i])]
        lead += 1

#def SettingIdentity(M, lead=0):
 #   if 