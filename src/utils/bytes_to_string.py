def bytes_to_string(byte_stream: bytes):
    """
    Converte um bytestream (sequência de bytes) em uma string.

    Parâmetros:
        byte_stream (bytes): O bytestream a ser convertido.

    Retorna:
        str: A string resultante da conversão.
    """
    # Em f'{byte:08b}' o f cria uma f-string, que permite inserir valores formatados dentro de {}
    # byte:08b formata o byte convertendo ele para binário (b) e garantindo que ele tenha 8 dígitos (08)
    return ''.join(f'{byte:08b}' for byte in byte_stream)