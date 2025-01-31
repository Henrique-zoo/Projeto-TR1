def string_to_byte_stream(input_string):
        """
        Converte uma string em um bitstream (sequência de bits).

        Parâmetros:
            input_string (str): A string de entrada para conversão.

        Retorna:
            bytes: Uma sequência de bytes representando o bitstream.
        """
        try:
            # Codifica a string em bytes ascii
            return input_string.encode('ascii')
        except UnicodeEncodeError as e:
            # Caso a string contenha caracteres não ascii, um erro será levantado
            print(f"Erro: A string contém caracteres não ascii. {e}")
            raise