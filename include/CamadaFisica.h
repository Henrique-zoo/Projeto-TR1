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
        std::vector<int> ask(std::string dig_signal, int a1, int a2, int sample);

    protected:

    private:
};

#endif // CAMADAFISICA_H
