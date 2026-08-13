#pragma once
#include <ap_fixed.h>
#include <cmath>

typedef ap_fixed<10, 2> input_t;
typedef ap_ufixed<16, 4> output_t;
typedef ap_fixed<16, 4> operation_t;

/// -------------------------------------
/// CPP's Standard Implementation
/// -------------------------------------
template<int N, int NEWTON> void cpp_exp(input_t value, output_t& resp)
{
    double input = value;
    double aux = exp(input);
    resp = (output_t) aux;
}

/// -------------------------------------
/// Pade's Approximants with division
/// -------------------------------------
template<int N> void pade_with_division(input_t value, output_t& resp, const operation_t paramsP[N + 1], const operation_t paramsQ[N + 1])
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

/// -------------------------------------
/// Pade's Approximants without Division
/// -------------------------------------
template<int N, int NEWTON> void pade_without_division(input_t value, output_t& resp, const operation_t paramsP[N + 1], const operation_t paramsQ[N + 1], const operation_t lut_newton[4])
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

    /// -------------------------------------
    /// newton-raphson to approximate 1 / den
    /// -------------------------------------

    ap_uint<2> msb = value.range(9, 8);
    output_t approx_frac = lut_newton[msb];

    for (int i = 0; i < NEWTON; i++)
    {
        #pragma HLS unroll
        approx_frac = approx_frac * (2 - den * approx_frac);
    }

    resp = num * approx_frac;
}

/// -------------------------------------
/// Maclaurin Series
/// -------------------------------------
template<int N> void maclaurin(input_t value, output_t& resp)
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

/// -------------------------------------
/// Piece Wise Implementation
/// -------------------------------------
template<int N> void piece_wise(input_t value, output_t& resp, const operation_t lut_values[(1 << N) + 2])
{
    #pragma HLS BIND_STORAGE variable=lut_values type=rom_1p impl=lutram

    ap_uint<N + 1> msb = value.range(9, 9 - N + 1) + value.range(9, 9);

    ap_ufixed<(10 - N), 0> lsb;
    lsb.range(9 - N, 0) = value.range(9 - N, 0);

    operation_t y1 = lut_values[msb];
    operation_t y2 = lut_values[msb + 1];

    resp = y1 + (y2 - y1) * lsb;
}