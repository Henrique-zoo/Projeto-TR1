#ifndef TRANSMISSOR_H
#define TRANSMISSOR_H

#include <string>
#include <vector>

class Transmissor
{
    public:
        Transmissor(double, double, double);
        virtual ~Transmissor();
        // Codificador de mensagem
        std::vector<bool> gerador_bit_stream(std::string);
        // Modulação Digital
        std::vector<int> nzr_polar(std::vector<bool>);
        std::vector<int> manchester(std::vector<bool>);
        std::vector<int> bipolar(std::vector<bool>);
        // Modulação por portadora
        std::vector<double> ask(std::vector<int>, int, int, int);
        std::vector<double> fsk(std::vector<int>, int, int, int);
        std::vector<double> psk(std::vector<int>, int, int, int);

    private:
        double amplitude, frequencia, fase;
        int modDigital, modPortadora;
};

#endif // TRANSMISSOR_H
