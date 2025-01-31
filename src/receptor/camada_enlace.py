from math import log2
from math import floor
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.utils import bytes_to_string

class CamadaEnlaceReceptor:
    def __init__(self):
        self.FLAG: bytes = bytes([22])
        self.ESC: bytes = bytes([27])
        self.CRC32_POLY = 0x04C11DB7  # Polinômio CRC-32 - IEEE 802

    # MÉTODOS DE DESENQUADRAMENTO
    def desenquadramento_contagem_de_caracteres(self, byte_stream: bytes) -> bytes:
        pacote: bytearray = bytearray()
        while byte_stream:
            # Lê o cabeçalho do quadro, que indica o tamanho do quadro
            length: int = int(byte_stream[0])
            # Remove o byte de comprimento do byte_stream
            byte_stream = byte_stream[1:]
            # Seleciona a carga útil do quadro
            frame = byte_stream[:length]
            # Remove o quadro do byte_stream
            byte_stream = byte_stream[length:]
            # Adiciona o quadro ao pacote
            pacote.extend(frame)
        return bytes(pacote)
    
    def desenquadramento_insercao_de_bytes(self, byte_stream: bytes) -> bytes:
        pacote: bytearray = bytearray()
        esc: bool = False
        while byte_stream:
            byte_atual = byte_stream[:1]  # Pega o primeiro byte
            byte_stream = byte_stream[1:]  # Remove o byte processado
            
            if byte_atual == self.FLAG and not esc:
                # Se for uma FLAG e não for precedida de ESC, ignora
                continue
            elif byte_atual == self.ESC and not esc:
                # Se for um ESC, ativa a flag e continua para o próximo byte
                esc = True
                continue
            else:
                # Se for um byte normal ou um byte após ESC, adiciona ao pacote
                pacote.extend(byte_atual)
                esc = False  # Reseta a flag ESC
            
        return bytes(pacote)

    # MÉTODOS DE VERIFICAÇÃO DE ERROS
    def verificar_bits_de_paridade(self, byte_stream: bytes) -> tuple[bytes, bool]:
        """
        Verifica os bits de paridade dos dados fornecidos.
        
        Args:
            byte_stream (bytes): Os dados para os quais os bits de paridade serão verificados.
        
        Returns:
            bool: True se os bits de paridade forem válidos, False caso contrário.
        """
        bit_stream: list[int] = [int(x) for x in bytes_to_string(byte_stream)]
        paridade = 0
        bit_stream_util = bit_stream[:-1]
        for bit in bit_stream_util:
            paridade ^= bit
            
        byte_stream_saida = bytes(int("".join(str(bit) for bit in bit_stream_util[i:i+8]), 2)   for i in range(0, len(bit_stream_util), 8))
        
        return byte_stream_saida, paridade == bit_stream[-1]
        
    def verificar_crc32(self, byte_stream: bytes) -> tuple[bytes, bool]:
        """
        Verifica o CRC-32 dos dados fornecidos.

        Args:
            byte_stream (bytes): Os dados para os quais o CRC-32 será verificado.
            tuple[bytes, bool]: A tupla contendo os dados sem o CRC-32 e um booleano indicando se o CRC-32 é válido.
        Returns:
            
        """
        # Extrai o CRC dos últimos 4 bytes do byte_stream
        crc_recebido: int = int.from_bytes(byte_stream[-4:], byteorder="big")
        byte_stream = byte_stream[:-4]

        crc_calculado: int = int.from_bytes(byte_stream, byteorder="big") << 32
        
        while crc_calculado.bit_length() >= 32:
            bytes_a_processar = (crc_calculado >> (crc_calculado.bit_length() - 32)) & 0xFFFFFFFF  
            if bytes_a_processar & 0x80000000:
                bytes_a_processar ^= self.CRC32_POLY
            else:
                bytes_a_processar ^= 0
            crc_calculado = ((bytes_a_processar & 0x7FFFFFFF) << (crc_calculado.bit_length() - 32)) | (crc_calculado & ((1 << (crc_calculado.bit_length() - 32)) - 1))

        return byte_stream, crc_calculado == crc_recebido

    # MÉTODOS DE CORREÇÃO DE ERROS
    def corrigir_hamming(self, encoded_bytes: bytes) -> tuple[bytes, bool]:
        """
        Decodifica uma sequência de bytes codificada com código de Hamming, detectando e corrigindo erros.
        
        Args:
            encoded_bytes (bytes): A sequência de bytes codificada com código de Hamming.
        
        Returns:
            tuple[bool, bytes]: Uma tupla contendo:
                - Um booleano indicando se um erro foi detectado.
                - A mensagem decodificada em bytes.
        """
        # Converte a sequência de bytes em uma lista de bits
        encoded_bits = ''.join(f'{byte:08b}' for byte in encoded_bytes)
        hamming_code = [int(bit) for bit in encoded_bits]
        
        r: int = 0  # Número de bits de paridade
        n: int = len(hamming_code)  # Número total de bits no código de Hamming
        
        # Calcula o número de bits de paridade
        while (2**r) < n + 1:
            r += 1
        
        # Verifica se há erros e corrige, se necessário
        error_position = 0
        for i in range(r):
            pos = 2**i  # Posição do bit de paridade (1-based index)
            paridade = 0
            for j in range(1, n + 1):
                if j & pos:  # Se o bit i está ativado em j
                    paridade ^= hamming_code[j - 1]
            if paridade != 0:
                error_position += pos
        
        # Se houver um erro, corrige o bit correspondente
        error_detected = error_position != 0
        if error_detected:
            print(f"Erro detectado na posição {error_position}. Corrigindo...")
            hamming_code[error_position - 1] ^= 1  # Inverte o bit errado
        
        # Remove os bits de paridade para obter a sequência de bits original
        original_bits = []
        for i in range(1, n + 1):
            if not log2(i).is_integer():  # Ignora os bits de paridade
                original_bits.append(str(hamming_code[i - 1]))
        
        # Converte a lista de bits de volta para bytes
        decoded_bits = ''.join(original_bits)
        decoded_bytes = bytes(int(decoded_bits[i:i+8], 2) for i in range(0, len(decoded_bits), 8))
        
        return (decoded_bytes, error_detected)