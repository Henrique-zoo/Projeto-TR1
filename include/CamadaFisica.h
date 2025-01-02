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
        // Modulacaoo Digital
        std::vector<int> nzr_polar(std::string bit_stream);
        std::vector<int> manchester(std::string bit_stream);
        std::vector<int> bipolar(std::string bit_stream);
        // Modulacao por portadora
        std::vector<int> ask(std::string dig_signal, int a1, int a2, int sample);
        std::vector<int> fsk(std::string dig_signal, int f1, int f2, int sample);
        std::vector<int> qam_mapping(std::string dig_signal);
        std::vector<int> qam8_modulation(std::string dig_signal, int sample);

    protected:

    private:
};

#endif // CAMADAFISICA_H
