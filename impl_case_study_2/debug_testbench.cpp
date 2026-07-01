#include <iostream>

#include "implementation.h"
#include "explore.h"

using namespace std;

int main (int argc, char **argv)
{
    input_t input = -2;
    input_t inc = 1;

    output_t resp;

    for (int i = 0; i < 4; i++)
    {
        cout << "input: " << input << endl;

        explore(input, resp);
        input += inc;

        cout << "resp: " << resp << endl;
    }

    return 0;
}