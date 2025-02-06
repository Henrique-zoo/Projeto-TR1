from math import sin, cos, ceil, pi

class CamadaFisicaTransmissor:
    def __init__(self, sample: int = 100, frequencia: float = 1.0, amplitude: float = 1.0, fase: float = 1.0) -> None:
        self.sample: int = sample
        self.frequencia: float = frequencia
        self.amplitude: float = amplitude
        self.fase: float = fase

    def gerador_bit_stream(self, mensagem: str) -> list[bool]:
        """
        Converte uma mensagem em um trem de bits (lista de booleanos).
        Verificamos se a mensagem só tem 0s e 1s, mas esse sempre será o caso
        """
        return [True if char == '1' else False for char in mensagem]

    # Modulação Digital
    def nrz_polar(self, bit_stream: list[bool]) -> list[int]:
        """
        Realiza a modulação NRZ-Polar (Non-Return-to-Zero).
        Converte True para 1 e False para -1.
        """
        return [1 if bit else -1 for bit in bit_stream]

    def manchester(self, bit_stream: list[bool]) -> list[int]:
        """
        Realiza a modulação Manchester.
        Codifica cada bit com o XOR entre o bit e o clock, alternando o clock a cada ciclo.
        """
        i: int = 0  # Índice do bit stream
        clk: bool = 0  # Estado inicial do clock
        dig_signal: list[int] = []  # Sinal digital gerado

        while i < len(bit_stream):  # Enquanto não processar todos os bits
            dig_signal.append(int(bit_stream[i] ^ clk))  # XOR do bit com o clock
            i += 1 * clk  # Incrementa o índice apenas quando o clock está em alta
            clk = not clk  # Alterna o estado do clock
        return dig_signal

    def bipolar(self, bit_stream: list[bool]) -> list[int]:
        """
        Realiza a modulação bipolar.
        Alterna entre +1 e -1 para bits 1, mantendo 0 para bits 0.
        """
        last_one: int = -1  # Último valor usado para bit 1 (+1 ou -1)
        dig_signal: list[int] = []

        for bit in bit_stream:
            if not bit:
                dig_signal.append(0)  # Adiciona 0 para bits 0
            else:
                last_one = -last_one  # Alterna o valor de last_one
                dig_signal.append(last_one)  # Adiciona +1 ou -1 para bits 1
        return dig_signal

    # Modulação por portadora
    def ask(self, dig_signal: list[int], mod_digital: str, amp_zero: int = 0, amp_one: int = 1) -> list[float]:
        """
        Realiza a modulação ASK (Amplitude Shift Keying).
        Modula o sinal digital utilizando diferentes amplitudes para 0 e 1.
        """
        signal: list[float] = [0.0] * (len(dig_signal) * self.sample)  # Inicializa o sinal modulado
        nrz_polar: bool = mod_digital == "NRZ-Polar"  # Verifica se a modulação digital é NRZ-Polar

        for i in range(len(dig_signal)):  # Para cada bit do sinal digital
            for j in range(self.sample):  # Gera amostras para cada bit
                t: float = j / self.sample
                if ((dig_signal[i] == 1 or dig_signal[i] == -1) and not nrz_polar) or dig_signal[i] == 1:
                    signal[i * self.sample + j] = amp_one * sin(2*pi*self.frequencia*t + self.fase)  # A * sen (2pi*f*t + ø) - sinal para 1 (ou -1 se não for NRZ-Polar)
                else:
                    signal[i * self.sample + j] = amp_zero * sin(2*pi*self.frequencia*t + self.fase)  # Sinal para 0 (ou -1 se for NRZ-Polar)
        return signal

    def fsk(self, dig_signal: list[int], mod_digital: str, f_zero: float = 0.0, f_one: float = 1.0) -> list[float]:
        """
        Realiza a modulação FSK (Frequency Shift Keying).
        Modula o sinal digital utilizando diferentes frequências para 0 e 1.
        """
        signal: list[float] = [0.0] * (len(dig_signal) * self.sample)  # Inicializa o sinal modulado
        nrz_polar: bool = mod_digital == "NRZ-Polar"  # Verifica se a modulação digital é NRZ-Polar

        for i in range(len(dig_signal)):  # Para cada bit do sinal digital
            for j in range(self.sample):  # Gera amostras para cada bit
                t: float = j / self.sample
                if ((dig_signal[i] == 1 or dig_signal[i] == -1) and not nrz_polar) or dig_signal[i] == 1:
                    signal[i * self.sample + j] = self.amplitude * sin(2*pi*f_one*t + self.fase)  # A * sen (2pi*f*t + ø) - sinal para 1 (ou -1 se não for NRZ-Polar)
                else:
                    signal[i * self.sample + j] = self.amplitude * sin(2*pi*f_zero*t + self.fase) # Sinal para 0 (ou -1 se for NRZ-Polar)
        return signal

    def qam8_modulation(self, dig_signal: list[int], mod_digital: str) -> list[float]:
        """
        Realiza a modulação 8-QAM.
        Modula o sinal digital utilizando uma constelação de 8 símbolos, cada um mapeado para um número complexo.
        """
        signal: list[float] = [0.0] * (ceil(len(dig_signal) / 3) * self.sample)  # Inicializa o sinal modulado
        constellation: dict[str, complex] = {
            "000": 1 + 1j, "001": 1 - 1j, "010": -1 + 1j,
            "011": -1 - 1j, "100": 1/3 + 1/3j, "101": 1/3 - 1/3j,
            "110": -1/3 + 1/3j, "111": -1/3 - 1/3j
        }

        while len(dig_signal) % 3:  # Preenche o bit stream com zeros para ser divisível por 3
            dig_signal.insert(0, 0)

        if mod_digital == "NRZ-Polar":  # Se a modulação digital for NRZ-Polar
            bit_stream: str = ''.join('1' if elemento == 1 else '0' for elemento in dig_signal)  # Cria uma string com base no sinal digital, colocando 0 no lugar de -1 para possibilitar o mapeamento na constelação QAM
        elif mod_digital == "Bipolar":  # Se a modulação digital for bipolar
            bit_stream: str = ''.join('1' if abs(elemento) == 1 else '0' for elemento in dig_signal)  # Cria uma string com base no sinal digital, colocando 0 no lugar de -1 para possibilitar o mapeamento na constelação QAM
        else: 
            bit_stream: str = ''.join('1' if elemento == 1 else '0' for elemento in dig_signal)  #  Cria uma string com base no sinal digital, colocando 0 no lugar de -1 para possibilitar o mapeamento na constelação QAM
        symbols: list[complex] = [constellation[bit_stream[i:i + 3]] for i in range(0, len(bit_stream), 3)]  # Mapeia os bits para os símbolos

        for i in range(len(symbols)):  # Para cada símbolo
            for j in range(self.sample):  # Gera amostras para o símbolo
                t: float = j / self.sample
                signal[i * self.sample + j] = symbols[i].real * cos(2*pi*self.frequencia*t) + symbols[i].imag * sin(2*pi*self.frequencia*t) # Gera o sinal com base na função S(t)=I⋅cos(2πft)+Q⋅sin(2πft)
        return signal
