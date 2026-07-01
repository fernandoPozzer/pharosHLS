#pragma once
#include <ap_fixed.h>
#include <cmath>

typedef ap_fixed<10, 2> input_t;
typedef ap_ufixed<16, 4> output_t;
typedef ap_fixed<16, 4> operation_t;

// operation_t padeP[3] = {1, 0.5, 0.08333333};
// operation_t padeQ[3] = {1, -0.5, 0.08333333};

template<int N, int NEWTON> void pade(input_t value, output_t& resp, const operation_t paramsP[N + 1], const operation_t paramsQ[N + 1], const operation_t lut_newton[4])
{
    operation_t num = paramsP[0];
    operation_t den = paramsQ[0];

    operation_t x = 1;
    
    for (int i = 1; i < N + 1; i++)
    {
        #pragma HLS PIPELINE off
        x *= value;

        num += x * paramsP[i];
        den += x * paramsQ[i];
    }

    /// newton-raphson para 1/den

    ap_uint<2> msb = value.range(9, 8);
    //std::cout << msb << std::endl;

    //const output_t lut_newton[4] = {1.3, 2.28, 0.51, 0.78};
    output_t approx_frac = lut_newton[msb];

    for (int i = 0; i < NEWTON; i++)
    {
        #pragma HLS unroll
        approx_frac = approx_frac * (2 - den * approx_frac);
    }

    resp = num * approx_frac;
}

template<int N, int NEWTON> void pade_without_unroll(input_t value, output_t& resp, const operation_t paramsP[N + 1], const operation_t paramsQ[N + 1], const operation_t lut_newton[4])
{
    operation_t num = paramsP[0];
    operation_t den = paramsQ[0];

    operation_t x = 1;
    
    for (int i = 1; i < N + 1; i++)
    {
        #pragma HLS PIPELINE off
        x *= value;

        num += x * paramsP[i];
        den += x * paramsQ[i];
    }

    /// newton-raphson para 1/den

    ap_uint<2> msb = value.range(9, 8);
    //std::cout << msb << std::endl;

    //const output_t lut_newton[4] = {1.3, 2.28, 0.51, 0.78};
    output_t approx_frac = lut_newton[msb];

    for (int i = 0; i < NEWTON; i++)
    {
        #pragma HLS PIPELINE off
        approx_frac = approx_frac * (2 - den * approx_frac);
    }

    resp = num * approx_frac;
}

template<int N, int NEWTON> void pade_with_division(input_t value, output_t& resp, const operation_t paramsP[N + 1], const operation_t paramsQ[N + 1])
{
    operation_t num = paramsP[0];
    operation_t den = paramsQ[0];

    operation_t x = 1;
    
    for (int i = 1; i < N + 1; i++)
    {
        #pragma HLS PIPELINE off
        x *= value;

        num += x * paramsP[i];
        den += x * paramsQ[i];
    }

    resp = num / den;
}

template<int N, int NEWTON> void cpp_exp(input_t value, output_t& resp)
{
    double input = value;
    double aux = exp(input);
    resp = (output_t) aux;
}

template<int N> void piece_wise(input_t value, output_t& resp, const operation_t lut_values[(1 << N) + 2])
{
    #pragma HLS BIND_STORAGE variable=lut_values type=rom_1p impl=lutram

    ap_uint<N + 1> msb = value.range(9, 9 - N + 1) + value.range(9, 9);

    //cout << "msb: " << msb << endl;

    ap_ufixed<(10 - N), 0> lsb;
    lsb.range(9 - N, 0) = value.range(9 - N, 0);

    // ap_ufixed<2 * (10 - N), (10 - N)> lsb = value.range(9 - N, 0);
    // lsb = lsb >> (10 - N);

    // cout << "LSB: " << value.range(9 - N, 0) << endl;
    //cout << "LSB frac: " << lsb << endl;

    //ap_ufixed<(10 - N), 0> lsb = value.range(9 - N, 0);
    // operation_t lsb = value.range(9 - N, 0);
    // operation_t lsb = (operation_t) 0.5;

    //const operation_t deltaX =  (operation_t)1 / (1 << N);

    //cout << "delta X: " << deltaX << endl;

    operation_t y1 = lut_values[msb];
    operation_t y2 = lut_values[msb + 1];

    //cout << "y2: " << y2 << endl;
    //cout << "y1: " << y1 << endl;

    resp = y1 + (y2 - y1) * lsb;
}


template<int N> void maclaurin(input_t value, output_t& resp, const operation_t coefficients[N])
{
    operation_t x = 1;
    resp = 1;

    for (int i = 0; i < N; i++)
    {
        #pragma HLS PIPELINE off
        x *= value * coefficients[i];
        resp += x;
    }
}

template<int N> void maclaurin_double(input_t value, output_t& resp, const double coefficients[N])
{
    double x = 1;
    double aux = 1;

    for (int i = 0; i < N; i++)
    {
        #pragma HLS PIPELINE off

        x *= (double)value * coefficients[i];
        aux += x;
    }

    resp = (output_t) aux;
}

template<int N> void maclaurin_coeff_on_demand(input_t value, output_t& resp)
{
    operation_t aux = 1;
    operation_t termo = 1;

    for (int n = 0; n < N; n++)
    {
        termo *= value / (n + 1);
        aux += termo;
    }

    resp = aux;
}