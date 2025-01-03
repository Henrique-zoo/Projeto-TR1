#include "Transmissor.h"
#include <vector>
#include <cmath>

Transmissor::Transmissor(double amplitude, double frequencia, double fase)
    : amplitude(amplitude), frequencia(frequencia), fase(fase), modDigital(0), modPortadora(0)
{}

Transmissor::~Transmissor() {}

std::vector<bool> Transmissor::gerador_bit_stream(std::string mensagem) {
    using namespace std;
    vector<bool> bit_stream;
    for (char letra : mensagem)
        bit_stream.push_back(letra - '0');

    return bit_stream;
}

std::vector<int> Transmissor::nzr_polar(std::vector<bool> bit_stream){
    using namespace std;
    modDigital = 1; // informamos que a modulação usada foi nzr polar
    vector<int> dig_signal;

    for(bool bit : bit_stream) {
        if (bit)
            dig_signal.push_back(1); // onde era 1 continua 1
        else
            dig_signal.push_back(-1); // onde era 0 agora é 1
    }
    return dig_signal;
}

std::vector<int> Transmissor::manchester(std::vector<bool> bit_stream){
    using namespace std;
    modDigital = 2; // informamos que a modulação usada foi a manchester
    vector<int> dig_signal;
    size_t i = 0;
    bool clk = 0;

    while (i < bit_stream.size()) { // repetimos o processo até i atingir t (quando o tamanho do vetor dig_signal for 2 vezes maior que o do vetor bit_stream)
        dig_signal.push_back(bit_stream[i] ^ clk); // colocamos o xor entre o clock e o bit de entrada no sinal de saída
        i += i * clk; // incrementamos i na batida do clock
        clk = !clk; // fazemos o clock bater a cada dois ciclos do while
    }

    return dig_signal;
}

std::vector<int> Transmissor::bipolar(std::vector<bool> bit_stream) {
    using namespace std;
    modDigital = 3; // informamos que a modulação usada foi a bipolar
    vector<int> dig_signal;
    int last1 = 0; // inicializamos a variável utilizada como flag

    for(size_t i = 0; i < bit_stream.size(); i++) { // percorremos o trem de bits original e
        if (!bit_stream[i])
            dig_signal.push_back(0); // onde era 0 continua 0
        else
            dig_signal.push_back(last1 = (last1 == 1) ? -1 : 1); // onde era 1 vira -1 se o 1 anterior continuou 1 e continua 1 se o 1 anterior virou -1
    }

    return dig_signal;
}

std::vector<double> Transmissor::ask(std::vector<int> dig_signal, int a0, int a1, int sample) {
    using namespace std;
    int qtd_bits = dig_signal.size();
    vector<double> signal(qtd_bits * sample, 1);
    bool nzr_polar = modDigital == 1; // checa se a modularização digital foi nzr-polar

    for (int i = 0; i < qtd_bits; i++) { // para cada int do sinal digital
        if (fabs(dig_signal[i]) && (!nzr_polar || dig_signal[i])) // verificamos se ele é 1 ou (-1 e não nzr-polar)
            for (int j = 0; j < sample; j++)
                signal[i * (sample-1) + j] = a1 * sin(2*M_PI*frequencia*j/sample + fase); // se for, a frequência do sinal resultante é f1 nesse intervalo
        else // se não for 1 ou -1 e não for nzr-polar, é 0; se for 1 e for nzr-polar, é -1
            for (int j = 0; j < sample; j++)
                signal[i * (sample-1) + j] = a0 * sin(2*M_PI*frequencia*j/sample + fase); // e a frequência do sinal resultante é f0 nesse intervalo
    }

    return signal;
}

std::vector<double> Transmissor::fsk(std::vector<int> dig_signal, int f0, int f1, int sample) {
    using namespace std;
    int qtd_bits = dig_signal.size();
    vector<double> signal(qtd_bits * sample, 1);
    bool nzr_polar = modDigital == 1; // checa se a modularização digital foi nzr-polar

    for (int i = 0; i < qtd_bits; i++) { // para cada int do sinal digital
        if (fabs(dig_signal[i]) && (!nzr_polar || dig_signal[i])) // verificamos se ele é 1 ou (-1 e não nzr-polar)
            for (int j = 0; j < sample; j++)
                signal[i * (sample-1) + j] = amplitude * sin(2*M_PI*f1*j/sample + fase); // se for, a frequência do sinal resultante é f1 nesse intervalo
        else // se não for 1 ou -1 e não for nzr-polar, é 0; se for 1 e for nzr-polar, é -1
            for (int j = 0; j < sample; j++)
                signal[i * (sample-1) + j] = amplitude * sin(2*M_PI*f0*j/sample + fase); // e a frequência do sinal resultante é f0 nesse intervalo
    }

    return signal;
}

std::vector<double> Transmissor::psk(std::vector<int> dig_signal, int p0, int p1, int sample) {
    using namespace std;
    int qtd_bits = dig_signal.size();
    vector<double> signal(qtd_bits * sample, 1);
    bool nzr_polar = modDigital == 1; // checa se a modularização digital foi nzr-polar

    for (int i = 0; i < qtd_bits; i++) { // para cada int do sinal digital
        if (fabs(dig_signal[i]) && (!nzr_polar || dig_signal[i])) // verificamos se ele é 1 ou (-1 e não nzr-polar)
            for (int j = 0; j < sample; j++)
                signal[i * (sample-1) + j] = amplitude * sin(2*M_PI*frequencia*j/sample + p1); // se for, a fase do sinal resultante é p1 nesse intervalo
        else // se não for 1 ou -1 e não for nzr-polar, é 0; se for 1 e for nzr-polar, é -1
            for (int j = 0; j < sample; j++)
                signal[i * (sample-1) + j] = amplitude * sin(2*M_PI*frequencia*j/sample + p0); // e a fase do sinal resultante é p0 nesse intervalo
    }
    
    return signal;
}
