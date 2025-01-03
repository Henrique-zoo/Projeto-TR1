#include <iostream>
#include "include/Transmissor.h"
#include "include/Receptor.h"
using namespace std;

int main() {
    double a, f, p;
    string mensagem;
    cin >> a >> f >> p;
    cout << "Forneça a mensagem de entrada\n";
    cin >> mensagem;
    Transmissor transmissor(a, f, p);
    vector<bool> tremDeBits = transmissor.gerador_bit_stream(mensagem);

    for (int bit : tremDeBits)
        cout << bit << " ";
    cout << endl;

    vector<int> nzr_polar = transmissor.nzr_polar(tremDeBits);
    vector<int> manchester = transmissor.manchester(tremDeBits);
    vector<int> bipolar = transmissor.bipolar(tremDeBits);

    cout << "O trem de bits após a modulação nzr polar é: ";
    for (int bit : nzr_polar)
        cout << bit << " ";
    cout << endl;

    cout << "O trem de bits após a modulação manchester é: ";
    for (int bit : manchester)
        cout << bit << " ";
    cout << endl;

    cout << "O trem de bits após a modulação manchester é: ";
    for (int bit : bipolar)
        cout << bit << " ";
    cout << endl;

    return 0;
}
