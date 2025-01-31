import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from tkinter import ttk
import math
import threading
from src.transmissor import CamadaFisicaTransmissor
from src.transmissor import CamadaEnlaceTransmissor
import socket
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from src.utils import string_to_byte_stream
from src.utils import bytes_to_string

class TRANSMISSOR_INTERFACE:
    def __init__(self):
        # Inicializa as variáveis para simular a rede
        self.mensagem: str = ""
        self.metodo_enquadramento: str = "Nenhum"
        self.metodo_deteccao_ou_correcao: str = "Nenhum"
        self.mod_digital: str = "Nenhum"
        self.mod_portadora: str = "Nenhum"
        self.enquadramento: str = "Nenhum"
        self.metodo_deteccao_ou_correcao: str = "Nenhum"
        self.sample: int = 0
        self.frequencia: float = -1.0
        self.amplitude: float = -1.0
        self.fase: float = -1.0
        self.amp_zero: float = -2.0
        self.amp_one: float = -1.0
        self.freq_zero: float = -2.0
        self.freq_one: float = -1.0
        
        # Criando a janela principal
        self.root = tk.Tk()
        self.root.title("Transmissor")  # Define o título da janela
        self.root.geometry("1350x800")  # Define o tamanho da janela
        self.root.resizable(True, True)  # Impede que a janela seja redimensionada
        self.cria_interface()
        # Executa o loop principal da interface
        self.root.mainloop()
        
    def enviar_para_o_receptor(self, wave, dig_signal):
        # Define server address and port
        HOST = '127.0.0.1'  # Localhost
        PORT = 65432        # Port to listen on
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                # Connect to the server
                client_socket.connect((HOST, PORT))
                print(f"Connected to {HOST}:{PORT}")
                # Prepare the message with protocol information and wave data
                wave_data = ", ".join(map(str, wave))
                extra_info = ""
                if self.mod_portadora == "ASK":
                    extra_info = f", {self.amp_zero}, {self.amp_one}"
                elif self.mod_portadora == "FSK":
                    extra_info = f", {self.freq_zero}, {self.freq_one}"
                elif self.mod_portadora == "8-QAM":
                    dig_data = "; ".join(map(str, dig_signal))
                    extra_info = f", {dig_data}"
                message = f"{self.sample}|{self.amplitude}|{self.frequencia}|{self.fase}|{self.mod_digital}|{self.mod_portadora}{extra_info}|{self.metodo_enquadramento}|{self.metodo_deteccao_ou_correcao}|{wave_data}|END_OF_SEQUENCE"
                for i in range(0, len(message), 1024):
                    try:
                        chunck = message[i: i + 1024].encode("ascii")
                    except UnicodeDecodeError as e:
                        chunck = "<ERROR>".encode("ascii")
                        print(f"Erro: Os bytes não puderam ser decodificados em ascii. {e}")
                    client_socket.sendall(chunck)
                        
            except ConnectionError as e:
                print(f"Connection failed: {e}")
        
    def cria_interface(self):
        
        self.pnl_menu = tk.Frame(self.root)  # Cria um frame para o menu
        self.pnl_menu.pack(side=tk.TOP, fill=tk.X, expand=True)  # Adiciona o frame do menu à janela principal

        self.pnl_mensagem = tk.Frame(self.pnl_menu)  # Cria um frame para a mensagem
        self.pnl_mensagem.grid(row=0, column=0, padx=10, pady=10, sticky="n")  # Adiciona o frame da mensagem ao menu

        self.lbl_mensagem = tk.Label(self.pnl_mensagem, text="Escreva uma mensagem:")  # Cria um label para a mensagem
        self.lbl_mensagem.grid(row=0, column=0, sticky="w")  # Adiciona o label ao frame da mensagem

        self.text_mensagem = tk.Entry(self.pnl_mensagem)  # Cria um campo de entrada para a mensagem
        self.text_mensagem.grid(row=1, column=0)  # Adiciona o campo de entrada ao frame da mensagem
        self.text_mensagem.bind("<Return>", lambda event: self.text_mensagem_action())  # Associa a função ao pressionar Enter

        self.btn_enviar = tk.Button(self.pnl_mensagem, text="Enviar", command=self.enviar_mensagem)  # Cria um botão de enviar
        self.btn_enviar.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="e")  # Adiciona o botão ao frame da mensagem

        self.lbl_mod_digital = tk.Label(self.pnl_mensagem, text="Selecione o tipo de modulação digital*:")  # Cria um label para modulação digital
        self.lbl_mod_digital.grid(row=2, column=0, columnspan=2, sticky="w")  # Adiciona o label ao frame da mensagem

        self.select_mod_digital = ttk.Combobox(self.pnl_mensagem, values=["Selecione um item", "NRZ-Polar", "Manchester", "Bipolar"], state="disabled")  # Cria um combobox para modulação digital
        self.select_mod_digital.current(0)  # Define o item padrão do combobox
        self.select_mod_digital.grid(row=3, column=0, columnspan=2, sticky="we")  # Adiciona o combobox ao frame da mensagem
        self.select_mod_digital.bind("<<ComboboxSelected>>", self.select_mod_digital_action)  # Associa a função ao selecionar um item

        self.lbl_mod_portadora = tk.Label(self.pnl_mensagem, text="Selecione o tipo de modulação por portadora*:")  # Cria um label para modulação por portadora
        self.lbl_mod_portadora.grid(row=4, column=0, columnspan=2, sticky="w")  # Adiciona o label ao frame da mensagem

        self.select_mod_portadora = ttk.Combobox(self.pnl_mensagem, values=["Selecione um item", "ASK", "FSK", "8-QAM"], state="disabled")  # Cria um combobox para modulação por portadora
        self.select_mod_portadora.current(0)  # Define o item padrão do combobox
        self.select_mod_portadora.grid(row=5, column=0, columnspan=2, sticky="we")  # Adiciona o combobox ao frame da mensagem
        self.select_mod_portadora.bind("<<ComboboxSelected>>", self.select_mod_portadora_action)  # Associa a função ao selecionar um item
        
        self.pnl_enlace = tk.Frame(self.pnl_menu)  # Cria um frame para o enlace
        self.pnl_enlace.grid(row=0, column=1, padx=10, pady=10, sticky="new")  # Adiciona o frame do enlace ao menu

        self.lbl_enquadramento = tk.Label(self.pnl_enlace, text="Selecione o método de enquadramento*:")  # Cria um label para enquadramento
        self.lbl_enquadramento.grid(row=0, column=0, columnspan=2, sticky="w")  # Adiciona o label ao frame do enlace

        self.select_enquadramento = ttk.Combobox(self.pnl_enlace, values=["Selecione um item", "Contagem de Caracteres", "Insercao de Bytes"], state="disabled")  # Cria um combobox para enquadramento
        self.select_enquadramento.current(0)  # Define o item padrão do combobox
        self.select_enquadramento.grid(row=1, column=0, columnspan=2, sticky="we")  # Adiciona o combobox ao frame do enlace

        self.lbl_deteccao = tk.Label(self.pnl_enlace, text="Selecione o método de detecção/correção de erro(s):")  # Cria um label para detecção de erro
        self.lbl_deteccao.grid(row=2, column=0, columnspan=2, sticky="w")  # Adiciona o label ao frame do enlace
        self.select_detecção = ttk.Combobox(self.pnl_enlace, values=["Selecione um item", "Bit de Paridade", "CRC-32", "Codigo de Hamming"], state="disabled")  # Cria um combobox para detecção de erro
        self.select_detecção.current(0)  # Define o item padrão do combobox
        self.select_detecção.grid(row=3, column=0, columnspan=2, sticky="we")  # Adiciona o combobox ao frame do enlace

        self.sliderErr = tk.Scale(self.pnl_enlace, label="Erro (‰)", orient='horizontal') # Slider para configurar erro
        self.sliderErr.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="we")

        self.pnl_config = tk.LabelFrame(self.pnl_menu, text="Configurações Padrão", borderwidth=2, relief="groove")  # Cria um frame para configuração com borda
        self.pnl_config.grid(row=0, column=2, padx=10, pady=10, sticky="ne")  # Adiciona o frame de configuração ao menu

        self.lbl_sample = tk.Label(self.pnl_config, text="Sample:")  # Cria um label para sample
        self.lbl_sample.grid(row=0, column=0, sticky="w", padx=5, pady=5)  # Adiciona o label ao frame de configuração
        self.txt_sample = tk.Entry(self.pnl_config)  # Cria um campo de entrada para sample
        self.txt_sample.grid(row=0, column=1, padx=5, pady=5)  # Adiciona o campo de entrada ao frame de configuração
        self.txt_sample.insert(0, "100")  # Insere um valor padrão no campo de entrada

        self.lbl_amplitude = tk.Label(self.pnl_config, text="Amplitude:")  # Cria um label para amplitude
        self.lbl_amplitude.grid(row=1, column=0, sticky="w", padx=5, pady=5)  # Adiciona o label ao frame de configuração
        self.text_amplitude = tk.Entry(self.pnl_config)  # Cria um campo de entrada para amplitude
        self.text_amplitude.grid(row=1, column=1, padx=5, pady=5)  # Adiciona o campo de entrada ao frame de configuração
        self.text_amplitude.insert(0, "1.0")  # Insere um valor padrão no campo de entrada

        self.lbl_frequencia = tk.Label(self.pnl_config, text="Frequência:")  # Cria um label para frequência
        self.lbl_frequencia.grid(row=2, column=0, sticky="w", padx=5, pady=5)  # Adiciona o label ao frame de configuração
        self.text_frequencia = tk.Entry(self.pnl_config)  # Cria um campo de entrada para frequência
        self.text_frequencia.grid(row=2, column=1, padx=5, pady=5)  # Adiciona o campo de entrada ao frame de configuração
        self.text_frequencia.insert(0, "1.0")  # Insere um valor padrão no campo de entrada
        
        self.lbl_fase = tk.Label(self.pnl_config, text="Fase:")  # Cria um label para fase
        self.lbl_fase.grid(row=3, column=0, sticky="w", padx=5, pady=5)  # Adiciona o label ao frame de configuração
        self.text_fase = tk.Entry(self.pnl_config)  # Cria um campo de entrada para fase
        self.text_fase.grid(row=3, column=1, padx=5, pady=5)  # Adiciona o campo de entrada ao frame de configuração
        self.text_fase.insert(0, "0.0")  # Insere um valor padrão no campo de entrada
        
        self.pnl_graficos = tk.Frame(self.root) # Cria um frame para os gráficos
        self.pnl_graficos.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True) # Configura o frame dos gráficos para preencher a janela
        
        self.frame_grafico_continuo = tk.Frame(self.pnl_graficos, width=600, height=400)
        self.frame_grafico_continuo.grid(row=1, column=2, padx=10, pady=10, sticky="n")
        self.criar_grafico_vazio(self.frame_grafico_continuo, "Sinal Pós-Modulação por Portadora")
        
        self.frame_grafico_discreto = tk.Frame(self.pnl_graficos, width=600, height=400)
        self.frame_grafico_discreto.grid(row=1, column=1, padx=10, pady=10, sticky="n")
        self.criar_grafico_vazio(self.frame_grafico_discreto, "Sinal Digital")
        
    def criar_grafico_vazio(self, frame: tk.Frame, titulo: str):
        fig, ax = plt.subplots()
        ax.set_title(titulo)
        ax.set_xlabel("Tempo")
        ax.set_ylabel("Amplitude")
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        toolbar = NavigationToolbar2Tk(canvas, frame)
        toolbar.update()
        canvas.get_tk_widget().pack()
        toolbar.pack()
        return canvas, ax
           
    def plota_grafico(self, dig_signal: list[int], wave: list[float]):
        """
        Desenha uma linha na tela baseada na onda fornecida usando matplotlib.
        """
        # Remove qualquer gráfico anterior
        for widget in self.frame_grafico_continuo.winfo_children():
            widget.destroy()

        # Cria a figura
        fig1, ax1 = plt.subplots()
        ax1.plot(wave, color='blue')
        ax1.set_title("Sinal Pós-Modulação por Portadora")
        ax1.set_xlabel("Tempo")
        ax1.set_ylabel("Amplitude")

        # Cria o canvas do Matplotlib e adiciona ao frame
        canvas1 = FigureCanvasTkAgg(fig1, master=self.frame_grafico_continuo)
        canvas1.draw()
        toolbar1 = NavigationToolbar2Tk(canvas1, self.frame_grafico_continuo)
        toolbar1.update()
        toolbar1.pack()
        canvas1.get_tk_widget().pack()
        
        for widget in self.frame_grafico_discreto.winfo_children():
            widget.destroy()
        
        fig2, ax2 = plt.subplots()
        ax2.step(range(len(dig_signal)), dig_signal, where='post', color='red')  # Desenha o gráfico com transições instantâneas
        ax2.set_title("Sinal Digital")
        ax2.set_xlabel("Tempo")
        ax2.set_ylabel("Amplitude")
        
        canvas2 = FigureCanvasTkAgg(fig2, master=self.frame_grafico_discreto)
        canvas2.draw()
        toolbar2 = NavigationToolbar2Tk(canvas2, self.frame_grafico_discreto)
        toolbar2.update()
        toolbar2.pack()
        canvas2.get_tk_widget().pack()
        
    def text_mensagem_action(self):
        # Função chamada quando uma mensagem é escrita
        self.select_enquadramento.config(state="readonly")  # Habilita o combobox de enquadramento
        self.select_detecção.config(state="readonly")  # Habilita o combobox de detecção de erro
        self.select_mod_digital.config(state="readonly")  # Habilita o combobox de modulação digital

    def select_mod_digital_action(self, event):
        # Função chamada quando um item é selecionado no combobox de modulação digital
        self.select_mod_portadora.config(state="readonly")  # Habilita o combobox de modulação por portadora
        
    def select_mod_portadora_action(self, event):
        mod_portadora = self.select_mod_portadora.get()
        
        if mod_portadora == "ASK":
            self.ask_frame = tk.Frame(self.pnl_mensagem)
            self.ask_frame.grid(row=6, column=0, columnspan=2, pady=10)
            tk.Label(self.ask_frame, text="Amplitude para 0:").grid(row=0, column=0, padx=10, sticky="w")
            self.text_amp_zero = tk.Entry(self.ask_frame)
            self.text_amp_zero.grid(row=0, column=1)
            self.text_amp_zero.insert(0, "0.0")
            tk.Label(self.ask_frame, text="Amplitude para 1:").grid(row=1, column=0, padx=10, sticky="w")
            self.text_amp_one = tk.Entry(self.ask_frame)
            self.text_amp_one.grid(row=1, column=1)
            self.text_amp_one.insert(0, "1.0")
        elif mod_portadora == "FSK":
            self.fsk_frame = tk.Frame(self.pnl_mensagem)
            self.fsk_frame.grid(row=6, column=0, columnspan=2, pady=10)
            tk.Label(self.fsk_frame, text="Frequência para 0:").grid(row=0, column=0, padx=10, sticky="w")
            self.text_freq_zero = tk.Entry(self.fsk_frame)
            self.text_freq_zero.grid(row=0, column=1)
            self.text_freq_zero.insert(0, "0.0")
            tk.Label(self.fsk_frame, text="Frequência para 1:").grid(row=1, column=0, padx=10, sticky="w")
            self.text_freq_one = tk.Entry(self.fsk_frame)
            self.text_freq_one.grid(row=1, column=1)
            self.text_freq_one.insert(0, "1.0")

    def enviar_mensagem(self):
        # Função chamada quando o botão de enviar é pressionado
        self.Bitstream = string_to_byte_stream(self.text_mensagem.get())
        self.err_value = self.sliderErr.get()
        self.mod_digital = self.select_mod_digital.get()
        self.mod_portadora = self.select_mod_portadora.get()
        self.metodo_enquadramento = self.select_enquadramento.get()
        self.metodo_deteccao_ou_correcao = self.select_detecção.get()
        self.sample = int(self.txt_sample.get())
        self.frequencia = float(self.text_frequencia.get())
        self.amplitude = float(self.text_amplitude.get())
        self.fase = float(self.text_fase.get())
        self.Fisica = CamadaFisicaTransmissor(self.sample, self.frequencia, self.amplitude, self.fase)
        self.Enlace = CamadaEnlaceTransmissor()
        
        byte_stream: bytes = bytes()
        # Faz o enquadramento da mensagem recebida
        if self.metodo_enquadramento == "Contagem de Caracteres":
            byte_stream = self.Enlace.contagem_de_caracteres(self.Bitstream)
        elif self.metodo_enquadramento == "Insercao de Bytes":
            byte_stream = self.Enlace.insercao_de_bytes(self.Bitstream)
        print(byte_stream)
        # Altera o bitstream de acordo com o método de detecção/correção de erro selecionado
        if self.metodo_deteccao_ou_correcao == "Bit de Paridade":
            byte_stream = self.Enlace.bit_de_paridade(byte_stream)
        elif self.metodo_deteccao_ou_correcao == "CRC-32":
            byte_stream = self.Enlace.crc32(byte_stream)
        elif self.metodo_deteccao_ou_correcao == "Codigo de Hamming":
            byte_stream = self.Enlace.hamming(byte_stream)
        else:
            byte_stream = bytes_to_string(byte_stream)
        print(byte_stream)    
        print(len(byte_stream))
            
        bit_stream: list[bool] = self.Fisica.gerador_bit_stream(byte_stream)
        bit_stream_para_enviar = self.inserir_error(bit_stream) # Insere erro na mensagem
        dig_signal: list[int] = []
        # Modula a mensagem de acordo com o método de modulação digital selecionado
        if self.mod_digital == "NRZ-Polar":
            dig_signal = self.Fisica.nrz_polar(bit_stream)
            dig_signal_para_enviar = self.Fisica.nrz_polar(bit_stream_para_enviar)
        elif self.mod_digital == "Manchester":
            dig_signal = self.Fisica.manchester(bit_stream)
            dig_signal_para_enviar = self.Fisica.manchester(bit_stream_para_enviar)
        elif self.mod_digital == "Bipolar":
            dig_signal = self.Fisica.bipolar(bit_stream)
            dig_signal_para_enviar = self.Fisica.bipolar(bit_stream_para_enviar)
            
        # Modula a mensagem de acordo com o método de modulação por portadora selecionado
        wave: list[float] = []
        if self.mod_portadora == "ASK":
            self.amp_zero = float(self.text_amp_zero.get())
            self.amp_one = float(self.text_amp_one.get())
            wave = self.Fisica.ask(dig_signal, self.mod_digital, self.amp_zero, self.amp_one)
            wave_para_enviar = self.Fisica.ask(dig_signal_para_enviar, self.mod_digital)
        elif self.mod_portadora == "FSK":
            self.freq_zero = float(self.text_freq_zero.get())
            self.freq_one = float(self.text_freq_one.get())
            print(f"{self.freq_zero}, {self.freq_one}")
            print(self.mod_digital)
            wave = self.Fisica.fsk(dig_signal, self.mod_digital, self.freq_zero, self.freq_one)
            wave_para_enviar = self.Fisica.fsk(dig_signal_para_enviar, self.mod_digital)
        elif self.mod_portadora == "8-QAM":
            dig_signal1 = dig_signal
            dig_signal2 = dig_signal_para_enviar
            wave = self.Fisica.qam8_modulation(dig_signal1, self.mod_digital)
            wave_para_enviar = self.Fisica.qam8_modulation(dig_signal2, self.mod_digital)
            
        self.plota_grafico(dig_signal, wave)
        self.enviar_para_o_receptor(wave_para_enviar, dig_signal_para_enviar)
        
    def inserir_error(self, bit_stream: list[bool]) -> list[bool]:
        """
        Insere erro na mensagem de acordo com o valor do slider.
        
        :param bit_stream: Mensagem a ser enviada
        :return: Mensagem com erro
        """
        erro = self.err_value
        for i in range(len(bit_stream)):
            if random.randint(0, 99) < erro / 10:
                bit_stream[i] = not bit_stream[i]
        return bit_stream
        