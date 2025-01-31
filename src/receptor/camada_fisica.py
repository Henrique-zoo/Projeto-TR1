from math import cos, sin, pi

class CamadaFisicaReceptor:
    def __init__(self, sample, amplitude, frequencia, fase) -> None:
        self.sample = sample
        self.amplitude = amplitude
        self.frequencia = frequencia
        self.fase = fase
    
    def decodificar_nrz_polar(self, dig_signal: list[int]) -> list[bool]:
        """
        Decodifica um sinal NRZ-Polar (Non-Return-to-Zero) para um trem de bits.
        Converte 1 para True e -1 para False.
        Args:
            dig_signal (list[int]): O sinal NRZ-Polar a ser decodificado.
        Returns:
            list[bool]: O trem de bits decodificado.
        """
        return [False if bit == -1 else True for bit in dig_signal]
    
    def decodificar_manchester(self, dig_signal: list[int]) -> list[bool]:
        """
        Decodifica um sinal Manchester para um trem de bits.
        Realiza o XOR entre o bit e o clock para decodificar.
        Args:
            dig_signal (list[int]): O sinal Manchester a ser decodificado.
        Returns:
            list[bool]: O trem de bits decodificado.
        """
        bit_stream: list[bool] = []
        i: int = 0
        while i < len(dig_signal):
            bit_stream.append(True if dig_signal[i] == 1 else False)  # Adiciona o bit atual ao bit stream
            i += 2
        return bit_stream
    
    def decodificar_bipolar(self, dig_signal: list[int]) -> list[bool]:
        """
        Decodifica um sinal bipolar para um trem de bits.
        Converte 0 para False e -1 para True.
        Args:
            dig_signal (list[int]): O sinal bipolar a ser decodificado.
        Returns:
            list[bool]: O trem de bits decodificado.
        """
        return [False if bit == 0 else True for bit in dig_signal]
    
    # ASK decoding
    def decodificar_ask(self, signal: list[float], mod_digital: str, amp_zero: float = 0, amp_one: float = 1) -> list[int]:
        """
        Decodifica um sinal de Chaveamento por Amplitude (ASK) em uma sequência binária.

        Args:
            signal (list[float]): O sinal ASK de entrada como uma lista de valores float.
            mod_digital (str): O tipo de modulação digital (NRZ-Polar, Bipolar, etc.).
            amp_zero (float, opcional): A amplitude que representa o binário 0. Padrão é 0.
            amp_one (float, opcional): A amplitude que representa o binário 1. Padrão é 1.

        Returns:
            list[int]: A sequência binária decodificada como uma lista de inteiros (0s e 1s).
        """
        if mod_digital == "NRZ-Polar":
            return [1 if max(signal[i:i+self.sample]) > (amp_zero + amp_one) / 2 else -1 for i in range(0, len(signal), self.sample)]
        elif mod_digital == "Bipolar":
            dig_signal: list[int] = []
            last_one = -1
            for i in range(0, len(signal), self.sample):
                if (max(signal[i:i+self.sample]) - amp_zero) > (max(signal[i:i+self.sample]) - amp_one):
                    last_one = -last_one
                    dig_signal.append(last_one)
                else:
                    dig_signal.append(0)
            return dig_signal
        else:
            return [1 if (max(signal[i:i+self.sample]) - amp_zero) > (max(signal[i:i+self.sample]) - amp_one) else 0 for i in range(0, len(signal), self.sample)]
    
    # FSK decoding function
    def decodificar_fsk(self, mod_signal: list[float], mod_digital: str, f_zero: float = 0.0, f_one: float = 1.0) -> list[int]:
        """
        Decodifica um sinal FSK modulado analisando a quantidade de cruzamentos de zero.

        Args:
            mod_signal (list[float]): O sinal FSK modulado.
            f_zero (float): A frequência usada para representar o bit 0.
            f_one (float): A frequência usada para representar o bit 1.
            sample (int): Número de amostras por bit.

        Returns:
            list[int]: O trem de bits decodificado.
        """
        bit_stream: list[int] = []
        # Percorre o sinal em janelas do tamanho de um bit
        for i in range(0, len(mod_signal), self.sample):
            janela: list[float] = mod_signal[i:i + self.sample]  # Extrai o trecho do sinal correspondente a um bit
            # Conta quantas vezes o sinal cruza o zero
            cruzamentos: int = 0
            for j in range(1, len(janela)):
                if (janela[j-1] < 0 and janela[j] > 0) or (janela[j-1] > 0 and janela[j] < 0):
                    cruzamentos += 1
            # Decide se o bit era 0 ou 1 baseado na frequência estimada
            if mod_digital == "NRZ-Polar":
                bit_stream.append(-1 if abs(cruzamentos - f_zero) < abs(cruzamentos - f_one) else 1)
            elif mod_digital == "Bipolar":
                last_one = -1
                if abs(cruzamentos - f_zero) > abs(cruzamentos - f_one):
                    last_one = -last_one
                    bit_stream.append(last_one)
                else:
                    bit_stream.append(0)
            else:
                bit_stream.append(0 if abs(cruzamentos - f_zero) < abs(cruzamentos - f_one) else 1) # Se a frequência estimada está mais próxima de f_zero, o bit é 0; caso contrário, é 1

        return bit_stream

    # 8-QAM decoding
    def decodificar_qam8(self, mod_signal: list[float], dig_modulation: str) -> list[int]:
        """
        Decodifica um sinal 8-QAM modulado e retorna a sequência de bits original.

        Args:
            mod_signal (list[float]): O sinal modulado em 8-QAM.
            frequencia (float): A frequência da portadora.
            sample (int): O número de amostras por símbolo.

        Returns:
            list[int]: O trem de bits decodificado.
        """
        # Define a constelação 8-QAM
        constellation: dict[complex, str] = {
            1 + 1j: "000",  1 - 1j:     "001",    -1 + 1j: "010",
            -1 - 1j: "011", 1/3 + 1/3j: "100", 1/3 - 1/3j: "101",
            -1/3 + 1/3j: "110",               -1/3 - 1/3j: "111"
        }

        # Lista de símbolos QAM
        symbols = list(constellation.keys())

        bit_stream: str = ""

        # Processa o sinal em blocos correspondentes a um símbolo
        for i in range(0, len(mod_signal), self.sample):
            bloco: list[float] = mod_signal[i:i + self.sample]  # Extrai um bloco de amostras
            
            # Estima os valores I e Q usando correlação
            I: float = sum(bloco[j] * cos(2 * pi * self.frequencia * (j / self.sample)) for j in range(len(bloco))) / self.sample # I (in-phase) é o valor médio de cada I em uma sample, em que I = S(t) * cos(2πft)
            Q: float = sum(bloco[j] * sin(2 * pi * self.frequencia * (j / self.sample)) for j in range(len(bloco))) / self.sample # Q (quadrature) é o valor médio de cada Q em uma sample, em que Q = S(t) * sin(2πft)
            simbolo_estimado: complex = complex(round(I, 1), round(Q, 1))  # round(x, 1) arredonda para 1 casa decimal

            # Encontra o símbolo da constelação mais próximo do estimado usando a distância euclidiana e lambda function
            simbolo_mais_proximo: complex = min(symbols, key=lambda s: abs(s - simbolo_estimado))
            
            # Converte o símbolo de volta para bits
            bit_stream += constellation[simbolo_mais_proximo]

        # Converte a string de bits para uma lista de inteiros (0s e 1s)
        bit_stream: list[bool] = [True if bit == '1' else False for bit in bit_stream]
        if dig_modulation == "NRZ-Polar":
            return [1 if bit else -1 for bit in bit_stream]
        elif dig_modulation == "Bipolar":
            last_one: int = 1  # Último valor usado para bit 1 (+1 ou -1)
            dig_signal: list[int] = []

            for bit in bit_stream:
                if not bit:
                    dig_signal.append(0)  # Adiciona 0 para bits 0
                else:
                    last_one = -last_one  # Alterna o valor de last_one
                    dig_signal.append(last_one)  # Adiciona +1 ou -1 para bits 1
            return dig_signal
        return [1 if bit else 0 for bit in bit_stream]