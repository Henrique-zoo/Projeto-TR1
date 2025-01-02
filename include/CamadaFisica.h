#ifndef CAMADAFISICA_H
#define CAMADAFISICA_H

#include <string>
#include <vector>

class CamadaFisica
{
    public:
        CamadaFisica();
        virtual ~CamadaFisica();
        // Codificador de mensagem
        std::vector<bool> gerador_bit_stream(std::string mensagem);
        // Modulação Digital
        std::vector<int> nzr_polar(std::vector<bool> bit_stream);
        std::vector<int> manchester(std::vector<bool> bit_stream);
        std::vector<int> bipolar(std::vector<bool> bit_stream);
        // Modulação por portadora
        std::vector<int> ask(std::vector<int> dig_signal, int a1, int a2, int sample);
        std::vector<int> fsk(std::vector<int> dig_signal, int f1, int f2, int sample);
        std::vector<int> psk(std::vector<int> dig_signal, int p1, int p2, int sample);

    protected:

    private:
};

#endif // CAMADAFISICA_H
