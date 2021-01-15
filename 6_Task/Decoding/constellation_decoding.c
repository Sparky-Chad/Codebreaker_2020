#include <bits/floatn-common.h>
#include <stdio.h>
#include <stdint.h>
#include <math.h>

// Union of data of uint16 or char[2]
union floating
{
    uint16_t float16;
    uint8_t bytes[2];
};

struct float16
{
    uint8_t sign;
    uint8_t exponent;
    uint16_t mantessa;
};

union floatUnion
{
    uint32_t decomp;
    float outport;
};

// Struct which has data sizes for regular float values
struct floatDecomposition
{
    uint32_t sign;
    uint32_t exponent;
    uint32_t mantessa;
};


// Convert from the half precision float to a single precision float
float convert_float(union floating);

// swap endianness
void swap_bytes(union floating);


/*
    This function is simply converting the union type using
    the pointer provided of the union type.
*/
void swap_bytes(union floating little)
{
    char bytes = little.bytes[0];
    little.bytes[0] = little.bytes[1];
    little.bytes[1] = little.bytes[0];
    return;
}


/*
    This function will take the float that is given and convert it into 
    a regular float value. This converts utilizing little endian format
*/
float convert_float(union floating half_precision)
{
    // instantiate 
    struct float16 import_float;

    union floatUnion f_float;

    // Create sign
    import_float.sign = half_precision.float16 & 0x0080;
    // Get the exponent
    import_float.exponent = half_precision.float16 & 0x007A;
    // get the mantessa
    import_float.mantessa = half_precision.float16 & 0xff03;
    // check if the float is abnormal
    // Check if signed zero
    if(import_float.exponent == 0)
    {
        if(import_float.mantessa > 0)
        {
            return (float)pow(-1, import_float.sign);
        }


        // If it is a zero return just a signed zero
        return (float)(0 * pow(-1, import_float.sign));
    }
    

}