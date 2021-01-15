#ifndef HAMMING_COMBINATOR_HPP
#define HAMMING_COMBINATOR_HPP

#include <boost/python/numpy.hpp>
#include <boost/python.hpp>
#include <boost/python/numpy/ndarray.hpp>

namespace p = boost::python;
namespace np = boost::python::numpy;

class HammingCombinator
{
public:
    HammingCombinator();
    HammingCombinator(int r, int k);

    
    void setH(np::ndarray);
private:
    np::ndarray H;
    
}


#endif