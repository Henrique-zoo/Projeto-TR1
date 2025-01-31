import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import socket
import threading
from src.receptor import CamadaEnlaceReceptor
from src.receptor import CamadaFisicaReceptor
from src.utils import listBool_to_bytes, bytes_to_string
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import numpy as np

class RECEPTOR_INTERFACE:
    def __init__(self) -> None:
        self.erro = True
        # Inicializa a variável de erro como False
        self.root = tk.Tk()  # Cria a janela principal
        self.root.title("Receptor")  # Define o título da janela
        self.root.geometry("1300x600")  # Define o tamanho da janela
        self.criar_interface()
        self.root.mainloop()

    def iniciar_servidor(self):
        thread = threading.Thread(target=self.abrir_servidor, daemon=True)
        thread.start()
        self.botao_abrir_servidor.config(text="Servidor Aberto...")
        self.botao_abrir_servidor.config(state="disabled")
    
    def abrir_servidor(self):
        HOST = '127.0.0.1'
        PORT = 65432

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        erro_decod = False
        try:
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            print(f"Server started at {HOST}:{PORT}")
            print("Waiting for a connection...")
            
            conn, addr = server_socket.accept()
            print(f"Connected by {addr}")
            mensagem_recebida = ""
            try:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        self.botao_abrir_servidor.config(text="Abrir Servidor")
                        self.botao_abrir_servidor.config(state="normal")
                        break  # Se não há mais dados, encerra a conexão
                    
                    string_recebida = data.decode("ascii")
                    mensagem_recebida += string_recebida
                    
                    if "END_OF_SEQUENCE" in string_recebida:
                        self.botao_abrir_servidor.config(text="Abrir Servidor")
                        self.botao_abrir_servidor.config(state="normal")
                        break
            except ConnectionResetError:
                print("A conexão foi encerrada pelo cliente.")
            finally:
                server_socket.close()
        except Exception as e:
            print(f"Erro no servidor: {e}")
        finally:
            server_socket.close()  # Garante que o socket do servidor seja fechado corretamente
        if not erro_decod:
            self.root.after(0, self.decodificar_mensagem, mensagem_recebida)
    
    def decodificar_mensagem(self, mensagem: str) -> str:
        mensagem = mensagem.split("|")
        sample = int(mensagem[0])
        amplitude = float(mensagem[1])
        frequencia = float(mensagem[2])
        fase = float(mensagem[3])
        modulacao: str = mensagem[4]
        portadora: str = mensagem[5].split(", ")
        enquadramento: str = mensagem[6]
        deteccao_correcao: str = mensagem[7]
        sinal: list[float] = [float(x) for x in mensagem[8].split(", ")]
        self.camada_fisica = CamadaFisicaReceptor(sample, amplitude, frequencia, fase)
        self.camada_enlace = CamadaEnlaceReceptor()
        dig_signal: list[int] = []
        print(mensagem)
        # Primeiro, decodifica o sinal analógico, retornando um sinal digital
        if portadora[0] == "ASK":
            amp_zero = float(portadora[1])
            amp_one = float(portadora[2])
            dig_signal = self.camada_fisica.decodificar_ask(sinal, modulacao, amp_zero, amp_one)
        elif portadora[0] == "FSK":
            freq_zero = float(portadora[1])
            freq_one = float(portadora[2])
            dig_signal = self.camada_fisica.decodificar_fsk(sinal, modulacao, freq_zero, freq_one)
        elif portadora[0] == "8-QAM":
            dig_signal = [int(x) for x in portadora[1].split("; ")]
        self.root.after(0, self.plota_grafico, dig_signal, sinal) # Plota os sinais
        print(dig_signal)
        print(len(dig_signal))
        # Em seguida, decodifica o sinal digital, retornando uma sequência de bits
        if modulacao == "NRZ-Polar":
            bit_stream = self.camada_fisica.decodificar_nrz_polar(dig_signal)
        elif modulacao == "Bipolar":
            bit_stream = self.camada_fisica.decodificar_bipolar(dig_signal)
        elif modulacao == "Manchester":
            bit_stream = self.camada_fisica.decodificar_manchester(dig_signal)
        # Transforma a sequência de bits (string) em bytes
        byte_stream = listBool_to_bytes(bit_stream)
        # Com o byte_stream em mãos, precisamos detectar/corrigir os erros, se necessário e desenquadrar a mensagem
        
        # Correção de erros
        if deteccao_correcao == "Codigo de Hamming": # Se Hamming foi selecionado no transmissor
            byte_stream, self.erro = self.camada_enlace.corrigir_hamming(byte_stream) # Corrige os erros
        # Detecção de erros
        elif deteccao_correcao == "Bit de Paridade": # Se Bit de Paridade foi selecionado no transmissor
            byte_stream, self.erro = self.camada_enlace.verificar_bits_de_paridade(byte_stream) # Verifica os bits de paridade
        elif deteccao_correcao == "CRC-32": # Se CRC-32 foi selecionado no transmissor
            byte_stream, self.erro = self.camada_enlace.verificar_crc32(byte_stream) # Verifica o CRC-32
        print(byte_stream)
        print(self.erro)
        pacote: bytes = bytes()
        if enquadramento == "Contagem de Caracteres":
            pacote = self.camada_enlace.desenquadramento_contagem_de_caracteres(byte_stream)
        elif enquadramento == "Insercao de Bytes":
            pacote = self.camada_enlace.desenquadramento_insercao_de_bytes(byte_stream)
        print(pacote)
        mensagem = pacote.decode("ascii")
        print(mensagem)
        self.text_mensagem.config(state="normal")  # Permitir edição temporária
        self.text_mensagem.delete(0, tk.END)  # Limpa qualquer texto anterior
        self.text_mensagem.insert(0, mensagem)  # Insere a nova mensagem
        self.text_mensagem.config(state="disabled")  # Bloqueia edição novamente
        self.detectou_erro.config(state="normal")
        self.detectou_erro.select() if not self.erro else self.detectou_erro.deselect()
        self.detectou_erro.config(state="disabled")


        
    def criar_interface(self):
        self.frame_mensagem = tk.Frame(self.root)
        self.frame_mensagem.grid(row=0, column=0, padx=10, pady=10)
        self.lbl_mensagem = tk.Label(self.frame_mensagem, text="Mensagem Recebida:")
        self.lbl_mensagem.grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.text_mensagem = tk.Entry(self.frame_mensagem, state="disabled")
        self.text_mensagem.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        self.lbl_detectou_erro = tk.Label(self.frame_mensagem, text="Erro Detectado:")
        self.lbl_detectou_erro.grid(row=0, column=4, stick="w", padx=5, pady=5)
        self.detectou_erro = tk.Checkbutton(self.frame_mensagem, state="disabled")
        self.detectou_erro.grid(row=0, column=5, sticky="w", padx=5, pady=5)
        
        self.botao_abrir_servidor = tk.Button(self.frame_mensagem, text="Abrir Servidor", command=self.iniciar_servidor)
        self.botao_abrir_servidor.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="we")
        
        self.pnl_graficos = tk.Frame(self.root)
        self.pnl_graficos.grid(row=1, column=0, padx=10, pady=10)
        
        self.frame_grafico_continuo = tk.Frame(self.pnl_graficos, width=600, height=400)
        self.frame_grafico_continuo.grid(row=1, column=0, padx=10, pady=10, sticky="n")
        self.criar_grafico_vazio(self.frame_grafico_continuo, "Sinal Recebido")
        
        self.frame_grafico_discreto = tk.Frame(self.pnl_graficos, width=600, height=400)
        self.frame_grafico_discreto.grid(row=1, column=1, padx=10, pady=10, sticky="n")
        self.criar_grafico_vazio(self.frame_grafico_discreto, "Sinal pós-demodulação por portadora")
        
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

RECEPTOR_INTERFACE()