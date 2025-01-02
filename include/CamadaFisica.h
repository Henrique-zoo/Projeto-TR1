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
        // Modula��o Digital
        std::vector<int> nzr_polar(std::string bit_stream);
        std::vector<int> manchester(std::string bit_stream);
        std::vector<int> bipolar(std::string bit_stream);
        // Modula��o por portadora
        std::vector<int> ask(std::string dig_signal, int a1, int a2, int sample);
        std::

    protected:

    private:
};

#endif // CAMADAFISICA_H
