#include "implementation.h"
#include "explore.h"

operation_t padeP[3] = {1.0000000000, 0.5000000000, 0.0833333333};

operation_t padeQ[3] = {1.0000000000, -0.5000000000, 0.0833333333};

operation_t newtonLUT[4] = {1.2972972973, 2.2857142857, 0.5161290323, 0.7868852459};



void explore (input_t& input, output_t& output)
{
	pade_without_unroll<2,1>(input,output,padeP,padeQ,newtonLUT);
}
