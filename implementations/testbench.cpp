#include <iostream>
#include <ostream>
#include <fstream>

#include "implementation.h"
#include "explore.h"

using namespace std;

int main (int argc, char **argv)
{
    ofstream output("output.txt");

    if(!output.is_open())
    {
        cout << "Could not open testbench's output file." << endl;
        return 1;
    }

    input_t input = -2;
    input_t inc = (input_t)1 >> 8;

    output_t resp;

    for (int i = 0; i < 1024; i++)
    {
        explore(input, resp);
        input += inc;

        output << resp << endl;
        //cout << resp << endl;
    }

    output.close();
    return 0;
}