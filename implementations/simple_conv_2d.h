#pragma once

template<
    int K,
    int P,
    int DIM,
    int CH_IN,
    int CH_OUT,
    int STRIDE,
    typename data_t>
void Conv2d(
    data_t input[CH_IN][DIM][DIM],
    data_t output[CH_OUT][(DIM - K + 2*P)/STRIDE + 1][(DIM - K + 2*P)/STRIDE + 1],
    data_t weights[CH_OUT][CH_IN][K][K],
    data_t bias[CH_OUT])
{
    const int PAD_DIM = DIM + 2 * P;
    const int OUT_DIM = (DIM - K + 2*P)/STRIDE + 1;

    data_t input_pad[CH_IN][PAD_DIM][PAD_DIM] = {};

    // for (int ci = 0; ci < CH_IN; ci++)
    // {
    //     #pragma HLS PIPELINE off

    //     for (int i = 0; i < PAD_DIM; i++)
    //     {
    //         #pragma HLS PIPELINE off

    //         for (int j = 0; j < PAD_DIM; j++)
    //         {
    //             #pragma HLS PIPELINE off
    //             input_pad[ci][i][j] = 0;
    //         }
    //     }
    // }

    for (int ci = 0; ci < CH_IN; ci++)
    {
        #pragma HLS PIPELINE off

        for (int i = 0; i < DIM; i++)
        {
            #pragma HLS PIPELINE off

            for (int j = 0; j < DIM; j++)
            {
                #pragma HLS PIPELINE off
                input_pad[ci][i + P][j + P] = input[ci][i][j];
            }
        }
    }

    for (int co = 0; co < CH_OUT; co++)
    {
        #pragma HLS PIPELINE off

        for (int i = 0; i < OUT_DIM; i++)
        {
            #pragma HLS PIPELINE off

            for (int j = 0; j < OUT_DIM; j++)
            {
                #pragma HLS PIPELINE off

                data_t acc = bias[co];

                for (int ci = 0; ci < CH_IN; ci++)
                {
                    #pragma HLS PIPELINE off

                    for (int ki = 0; ki < K; ki++)
                    {
                        #pragma HLS PIPELINE off

                        for (int kj = 0; kj < K; kj++)
                        {
                            #pragma HLS PIPELINE off

                            int in_i = i * STRIDE + ki;
                            int in_j = j * STRIDE + kj;

                            acc += input_pad[ci][in_i][in_j] * weights[co][ci][ki][kj];
                        }
                    }
                }

                output[co][i][j] = acc;
            }
        }
    }
}
