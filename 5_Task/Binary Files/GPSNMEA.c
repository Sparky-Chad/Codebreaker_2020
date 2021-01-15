#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

#define FIFO "/tmp/gps_fifo"

#define STD_BUFFER 200


int* GPSNMEA();
// main will get the character and then print
int main()
{
    int* b = GPSNMEA();
    for(int i = 0; b[i] != 0; i++)
    {
        printf("%c", (char)b[i]);
    }
    free(b);
    
    return 0;
}
int *GPSNMEA() 
{
    // Create file buffer, char and int to return
    FILE *ifile;
    int *buffer;
    int *output;
    char c;
    int counter;
    
    buffer = malloc(STD_BUFFER * sizeof(int));
    for(int i = 0; i < STD_BUFFER; i++)
    {
        buffer[i] = 0;
    }
    
    ifile = fopen(FIFO, "r");
    while( (c = fgetc(ifile)) != 0 && counter < STD_BUFFER)
    {
        buffer[counter++] = (int)c;
        if(c == '\n') { break; }
    }
    
    // Close the file
    fclose(ifile);
    
    // Write slimmer output
    output = malloc( (counter+1) * sizeof(int));
    
    for(int i = 0; buffer[i] != 0; i++)
    {
        output[i] = buffer[i];
    }
    // Null terminate
    output[counter] = 0;
    
    // Don't hang you damn pointers
    free(buffer);
    
    //if(buffer == '\0') return 64;
    return output;
} 

// A struct to more easily pass information through the fifo
/*
struct lineread
{
    // Contains the size of the char buffer it points to
    int size;
    char* buffer;
};
int gpsnmea_counter = 0;
int *GPSNMEA();
struct lineread readline(FILE* ifile, char* buffer);
*/

/*
int main() {
    char *c;
    
    c = GPSNMEA();
    
    for(int i = 0; c[i] != '\0'; i++)
    {
        printf("%c", c[i]);
    }
    
    // free c
    free(c);
} */


/*
// Fake gpsoutput, reading characters from fifo
int *GPSNMEA() {
    // set up file reader object
    FILE *ifile;
    long filelen;
    char *buffer;
    int *output;
    int a;
    struct lineread temp;
    
    ifile = fopen(FIFO, "r");
    filelen = 64;
    
    // Initial buffer which will serve to initially hold the string
    buffer = (char *)malloc(100 * sizeof(char));
    temp = readline(ifile, buffer);
    
    // create slim output buffer with extra character to null terminate the string
    output = malloc((temp.size+1) * sizeof(int));
    
    // close file reader
    fclose(ifile);
    
    // copy from buffer to slim output
    for(int i = 0; i < temp.size-1; i++)
    {
        output[i] = (int)buffer[i];
    }
    // Null terminate the string
    output[temp.size - 1] = (int)'\0';
    
    // Now free up buffer so no hanging pointers
    free(buffer);
    
    // return output
    return (int *)output;
}

struct lineread readline(FILE* ifile, char *buffer)
{
    char c;
    int counter = 0;
    struct lineread temp = {0, buffer};
    // loop through file buffer passing chars to the buffer until '\n' is caught
    while((c = fgetc(ifile)) != 0) 
    {
        buffer[counter++] = c;
        temp.size = counter;
        if(c == '\n') { break; }
    }
    return temp;
} */
EXPORT_SYMBOL(GPSNMEA);
