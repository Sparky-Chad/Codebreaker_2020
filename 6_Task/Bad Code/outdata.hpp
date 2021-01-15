#ifndef OUTDATA_H
#define OUTDATA_H

#include <bitset>

using namespace std;
/*
 * This file will define the "outdata" type which will be a union
 * type. This will hold a *32* bit unsigned integer, stored as a macro
 * for if this needs to change in the future
 */

class Outdata {
private:
  bitset<32> buffer;
  bitset<16> 



#endif
