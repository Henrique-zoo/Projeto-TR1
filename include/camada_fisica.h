#ifndef CAMADA_FISICA_H
#define CAMADA_FISICA_H

#include <string>
#include <vector>

class camada_fisica
{
    public:
        camada_fisica();
        virtual ~camada_fisica();
        std::vector<int> nzr_polar(std::string bit_stream);
        std::vector<int> manchester(std::string bit_stream);
        std::vector<int> bipolar(std::string bit_stream);
        std::vector<int> ask();

    protected:

    private:
};

#endif // CAMADA_FISICA_H
