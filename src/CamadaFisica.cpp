#include "CamadaFisica.h"
#include <vector>;
using namespace std;

vector<int> CamadaFisica::nzr_polar(vector<bool> bit_stream){
    vector<int> dig_signal;
    for(bool bit : bit_stream) {
        if (bit)
        {
            dig_signal.push_back(1);
        }
        else
        {
            dig_signal.push_back(-1);
        }

    }
}

CamadaFisica::CamadaFisica()
{
    //ctor
}

CamadaFisica::~CamadaFisica()
{
    //dtor
}
