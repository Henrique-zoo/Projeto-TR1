from math import floor, log2

class CamadaEnlaceTransmissor:
    def __init__(self) -> None:
        # Definição de constantes para flags e polinômio CRC
        self.FLAG: bytes = bytes([22])
        self.ESC: bytes = bytes([27])
        self.CRC32_POLY: int = 0x04C11DB7  # Polinômio CRC-32 - IEEE 802 (0000 0100 1100 0001 0001 1101 1011 0111)
    
    # MÉTODOS DE ENQUADRAMENTO
    def contagem_de_caracteres(self, byte_stream: bytes, maxFrameSize: int = 4) -> bytes:
        """
        Realiza a contagem de caracteres em um fluxo de bytes e divide-o em quadros (frames) de tamanho máximo especificado.

        Args:
            byte_stream (bytes): O fluxo de bytes a ser dividido em quadros.
            maxFrameSize (int): O tamanho máximo de cada quadro em bytes.

        Returns:
            bytes: Uma sequência de bytes contendo os quadros codificados, onde cada quadro é precedido por um byte que indica seu comprimento.
        """
        # Utilizamos bytearray para manipular os bytes (bytes é um objeto imutável)
        frames: bytearray = bytearray()
        while byte_stream:
            # Define o quadro como o máximo de bytes possíveis
            frame: bytes = byte_stream[:maxFrameSize]
            # Atualiza o fluxo de bytes, removendo os bytes já processados
            byte_stream = byte_stream[maxFrameSize:]
            # Adicionar o comprimento como um único byte (o append do bytearray já faz a conversao de int para byte)
            frames.append(len(frame))
            # O extend adiciona ao final do bytearray bytes ou um iterável de inteiros
            frames.extend(frame)
        
        return bytes(frames)
    
    def insercao_de_bytes(self, byte_stream: bytes, maxFrameSize: int = 4) -> bytes:
        """
        Realiza a inserção de bytes em um fluxo de bytes e divide-o em quadros (frames) de tamanho máximo especificado.
        
        Args:
            byte_stream (bytes): O fluxo de bytes a ser dividido em quadros.
            maxFrameSize (int): O tamanho máximo de cada quadro.
        
        Returns:
            bytes: Uma sequência de bytes contendo os quadros codificados, em que cada carga útil (sequência de bytes de tamanho especificado) é precedida e sucedida por um byte de flag.
        """
        frames: bytearray = bytearray()
        while byte_stream:
            # Adiciona a flag inicial ao quadro
            frames.extend(self.FLAG)
            i: int = 0
            while i < maxFrameSize and byte_stream:
                # Verifica se a sequência atual é uma FLAG ou ESC, se for, insere um ESC antes
                if byte_stream[:1] == self.FLAG or byte_stream[:1] == self.ESC:
                    frames.extend(self.ESC)
                # Adiciona o byte atual ao dado enquadrado
                frames.extend(byte_stream[:1])
                # Atualiza o byte_stream, retirando o byte já processado
                byte_stream = byte_stream[1:]
                i += 1
            frames.extend(self.FLAG)
        
        return bytes(frames)
    
    
    # MÉTODOS DE DETECÇÂO DE ERROS
    def bit_de_paridade(self, byte_stream: bytes) -> str:
        """
        Utiliza-se paridade par
        Calcula o bit de paridade para os dados fornecidos e anexa o bit de paridade ao final dos dados.

        Args:
            byte_stream (bytes): Os dados para os quais o bit de paridade será calculado.

        Returns:
            bytes: O byte_stream com o bit de paridade anexado ao final.
        """
        # Converte os bytes em uma lista de inteiros (0 ou 1)
        bit_stream: list[int] = [int(x) for x in ''.join(f'{byte:08b}' for byte in byte_stream)] + [0]  # Adiciona um bit extra para o bit de paridade
        # Fazemos o XOR entre todos os bits para obter o bit de paridade
        for bit in bit_stream[:-1]:
            bit_stream[-1] ^= bit
            
        return ''.join(str(bit) for bit in bit_stream) # Retorna os dados originais com o bit de paridade anexado ao final
    
    def crc32(self, byte_stream: bytes) -> str:
        """
        Calcula o CRC-32 manualmente para os dados fornecidos e anexa o valor CRC-32 ao início dos dados.

        Args:
            byte_stream (bytes): Os dados para os quais o CRC-32 será calculado.

        Returns:
            bytes: O byte_stream com o valor CRC-32 anexado ao início.
        """
        bit_stream: str = ''.join(f'{byte:08b}' for byte in byte_stream) # Cada byte vira 8 bits
        crc: int = int.from_bytes(byte_stream, byteorder="big") << 32  # Adiciona 32 bits de 0 ao final dos dados
        
        while crc.bit_length() >= 32:
            bytes_a_processar = (crc >> (crc.bit_length() - 32)) & 0xFFFFFFFF  # Obtém os 32 bits mais à esquerda, deslocando o bit stream para a direita de forma a deixar apenas os 32 bits mais à esquerda (O deslocamento >> já deveria fazer isso, mas por garantia, fazemos um AND com 0xFFFFFFFF, que é uma sequência binária de 32 bits com todos os bits iguais a 1)
            if bytes_a_processar & 0x80000000:  # Se o bit mais à esquerda for 1, faz XOR com o polinômio
                bytes_a_processar ^= self.CRC32_POLY
            else:  # Se o bit mais à esquerda for 0, faz XOR com 0 (não altera)
                bytes_a_processar ^= 0 # Poderíamos não fazer nada, mas para que a implementação seja mais clara, fazemos o XOR com 0

            # Como o resultado do XOR é um int de 32 bits, esse loop realizaria infinitamente o XOR entre os mesmos valores, para a implementação correta, é necessário ignorar o bit mais significativo
            crc = ((bytes_a_processar & 0x7FFFFFFF) << (crc.bit_length() - 32)) | (crc & ((1 << (crc.bit_length() - 32)) - 1)) # Fazemos isso da seguinte forma: fazemos um AND com 0x7FFFFFFF para ignorar o bit mais significativo e depois deslocamos os bits para a esquerda para que o bit diferente de 0 mais à direita seja o bit menos significativo do resultado do XOR. Depois, fazemos um OR com os bits restantes do CRC original, para que o resultado seja a concatenação dos bits do XOR com os bits restantes do CRC original - realizaremos esse processo por todo o bit_stream original, até chegarmos ao crc final

        return bit_stream + f"{crc:032b}"  # Retorna os dados originais com o CRC anexado ao final

    # MÉTODOS DE CORREÇÃO DE ERROS
    def hamming(self, byte_stream: bytes) -> str:
        """
        Gera uma bitstream com código de Hamming aplicado recebendo uma sequência de bytes.
        
        Args:
            byte_stream (bytes): A sequência de bytes a ser codificada.
        
        Returns:
            str: A sequência de bits com o código de Hamming aplicado.
        """
        # Converte a sequência de bytes em uma lista de bits
        bit_stream: list[int] = [int(bit) for byte in byte_stream for bit in f'{byte:08b}']
        
        m: int = len(bit_stream)  # Número de bits de dados
        r: int = 0  # Número de bits de paridade
        
        # Calcula quantos bits de paridade são necessários
        while (2**r) < (m + r + 1):
            r += 1
        
        # Cria a lista que contém os bits de dados e espaços para os bits de paridade
        hamming_code: list[int] = []
        j = 0  # Índice para bit_stream original
        
        # Preenche a lista com os bits de dados e espaços para os bits de paridade
        for i in range(1, m + r + 1):
            if log2(i).is_integer():
                hamming_code.append(0)  # Inicializa os bits de paridade com 0
            else:
                hamming_code.append(bit_stream[j])
                j += 1
        
        # Cálculo dos bits de paridade
        for i in range(r):
            pos = 2**i  # Posição do bit de paridade (1-based index)
            paridade = 0
            for j in range(1, len(hamming_code) + 1):
                if j & pos:  # Se o bit i está ativado em j
                    paridade ^= hamming_code[j - 1]
            hamming_code[pos - 1] = paridade  # Definimos o bit de paridade correto
        
        return ''.join(str(bit) for bit in hamming_code)  # Retorna a string com código de Hamming