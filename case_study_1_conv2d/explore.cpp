#include "implementation.h"
#include "explore.h"

void explore (type_t input[3][20][20], type_t output[14][20][20])
{
	Conv2d<5,2,20,3,14,1>(input,output,weight,bias);
}
