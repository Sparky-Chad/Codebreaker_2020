#include <cmath>
#include <../half_precision/half.hpp>
#include <fstream>
#include <vector>

using namespace std;

float extract_sample(fstream&);

int main();


int main() 
{
  // file buffer
  ifstream ifile("../signal.ham", ifstream::in | ifstream::binary);
  // buffer to hold input for the half precision floating point
  half_precision::half buffer;


  
}


