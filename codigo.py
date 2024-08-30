import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from fractions import Fraction as Fr
import random

class Info:
    ALUNO = 'Célio Vieira de Lima Júnior'
    DISCIPLINA = 'Álgebra Linear'
    PROJETO = 'Proj. Método Gauss Jordan - Matriz Condensada'
    PROFESSOR = 'Rafael Barbosa da Silva'

    @staticmethod
    def apresentacao():
        return f"Professor: {Info.PROFESSOR}\n\nProjeto: {Info.PROJETO}\n\nAluno: {Info.ALUNO}\n\nDisciplina: {Info.DISCIPLINA}"


class Utils:
    def centralizar_janela(janela):
        janela.update_idletasks()
        largura_janela = janela.winfo_width()
        altura_janela = janela.winfo_height()
        largura_tela = janela.winfo_screenwidth()
        altura_tela = janela.winfo_screenheight()
        x = (largura_tela // 2) - (largura_janela // 2)
        y = (altura_tela // 2) - (altura_janela // 2)
        janela.geometry(f"{largura_janela}x{altura_janela}+{x}+{y}")


class MatrizCondensadaEscada:
    def __init__(self, matriz):
        self.matriz = [[Fr(valor) for valor in linha] for linha in matriz]

    def encontrar_pivo(self, coluna, linha_inicio):
        max_row = max(range(linha_inicio, len(self.matriz)), key=lambda r: abs(self.matriz[r][coluna]))
        return max_row

    def normalizar_linha(self, linha, coluna):
        pivot = self.matriz[linha][coluna]
        if pivot != 0:
            self.matriz[linha] = [x / pivot for x in self.matriz[linha]]

    def eliminar_linhas(self, linha, coluna):
        for i in range(len(self.matriz)):
            if i != linha:
                fator = -self.matriz[i][coluna]
                if fator != 0:
                    self.matriz[i] = [self.matriz[i][j] + fator * self.matriz[linha][j] for j in range(len(self.matriz[i]))]

    def condensar(self):
        linhas = len(self.matriz)
        colunas = len(self.matriz[0])
        pivot_col = 0
        for i in range(min(linhas, colunas)):
            if pivot_col >= colunas:
                break            
            
            max_row = self.encontrar_pivo(pivot_col, i)
            if self.matriz[max_row][pivot_col] == 0:
                pivot_col += 1
                continue

            if max_row != i:
                self.matriz[i], self.matriz[max_row] = self.matriz[max_row], self.matriz[i]

            self.normalizar_linha(i, pivot_col)
            self.eliminar_linhas(i, pivot_col)
            pivot_col += 1
        return self.matriz

    def imprimir_matriz(self):
        output = str([[str(valor) for valor in linha] for linha in self.matriz]).replace('\'', '')
        print(output)

class Aplicacao:
    ERRO_OBTER_VALOR_MATRIZ = "Não foi possível obter os valores da matriz. Verifique se há algum valor não numérico"
    ESTADO_DESABILITADO = {
        'state': 'disabled',
        'cursor': 'X_cursor'
    }
    ESTADO_NORMAL = {
        'state': 'normal',
        'cursor': ''
    }
    CONVERSORES_MODO = {
        1: lambda valor: round(float(valor), 2),
        2: lambda valor: valor,
    }

    def __init__(self, janela):
        self.modos = {
            1: 'Decimal arredondado para 2 casas',
            2: 'Números representados como frações',
        }
        self.modo_selecionado = tk.IntVar(value=1)
        self.modo_selecionado.trace_add(["write"], lambda *_: self.alterar_modo_saida())
        self.modo_selecionado_display = tk.StringVar(value=self.modos[1])

        menu = tk.Menu(tearoff=0)
        for value, label in self.modos.items():
            menu.add_radiobutton(label=label, value=value, variable=self.modo_selecionado)

        self.janela = janela
        self.matriz = None
        self.max_size = (6, 6)
        self.numero_linhas = tk.IntVar(self.janela, value=3)
        self.numero_colunas = tk.IntVar(self.janela, value=3)
        self.numero_colunas.trace_add("write", self.desenhar_matriz)
        self.numero_linhas.trace_add("write", self.desenhar_matriz)
        
        self.painel_horizontal = tk.Frame(self.janela)
        self.painel_horizontal.pack(fill='both')
        self.container_matriz = tk.LabelFrame(self.painel_horizontal, width=232, height=157, text='Matriz de origem:')
        self.container_matriz.pack(side='left')
        self.container_matriz.grid_propagate(False)

        self.container_resultado = tk.LabelFrame(self.painel_horizontal, width=334, height=157, text='Matriz Escalonada:')
        self.container_resultado.pack(expand=True, side='right')
        self.container_resultado.grid_propagate(False)

        self.painel = tk.LabelFrame(self.janela, text='Configurações')
        self.painel.columnconfigure(1, weight=1)        
        self.painel.pack(side='bottom', fill='x')

        self.label_modo = tk.Label(self.painel, text='Modo de saída:')
        self.label_modo.grid(row=0, column=0, sticky='sw')
        self.modo_combobox = ttk.Menubutton(self.painel, textvariable=self.modo_selecionado_display)
        self.modo_combobox.configure(menu=menu)
        self.modo_combobox.grid(row=0, column=1, sticky='nsew')
        
        self.label_numero_linhas = tk.Label(self.painel, text='Número de linhas:')
        self.label_numero_linhas.grid(row=1, column=0, sticky='sw')
        self.campo_numero_linhas = tk.Scale(self.painel, orient='horizontal', variable=self.numero_linhas, from_=2, to=6)
        self.campo_numero_linhas.grid(row=1, column=1, sticky='nsew')
        
        self.label_numero_colunas = tk.Label(self.painel, text='Número de colunas:')
        self.label_numero_colunas.grid(row=2, column=0, sticky='sw')
        self.campo_numero_colunas = tk.Scale(self.painel, orient='horizontal', variable=self.numero_colunas, from_=2, to=6)
        self.campo_numero_colunas.grid(row=2, column=1, sticky='nsew')

        self.painel_acoes = tk.Frame(self.painel)
        self.painel_acoes.grid(columnspan=2, sticky='nsew')
        
        self.escalonar_btn = tk.Button(self.painel_acoes, text='Escalonar', command=self.realizar_escalonamento, bg='green', fg='white')
        self.escalonar_btn.pack(fill='x', side='left', expand=True, padx=(0, 4), pady=(16, 4))

        self.randomizar_btn = tk.Button(self.painel_acoes, text='Randomizar', command=self.randomizar, bg='yellow')
        self.randomizar_btn.pack(fill='x', side='left', expand=True, padx=(0, 4), pady=(16, 4))
        
        self.limpar_btn = tk.Button(self.painel_acoes, text='Limpar', command=self.limpar, bg='red', fg='white')
        self.limpar_btn.pack(fill='x', side='left', expand=True, padx=(0, 4), pady=(16, 4))
        self.limpar_btn.configure(**self.ESTADO_DESABILITADO)
        
        self.janela.after(20, self.exibir_ajuda)
        self.desenhar_matriz()
        self.realizar_escalonamento_automatico()

    def exibir_ajuda(self):
        messagebox.showinfo(title='Sobre', message=Info.apresentacao())

    def limpar_matriz(self):
        for children in self.container_matriz.winfo_children():
            children.destroy()

    def desenhar_matriz(self, *_):
        self.limpar_matriz()
        for linha in range(self.numero_linhas.get()):
            for coluna in range(self.numero_colunas.get()):
                campo = tk.Entry(self.container_matriz, width=5)
                campo.insert('end', '0')
                campo.grid(row=linha, column=coluna, padx=2, pady=2)

    def limpar_resultado(self):
        for children in self.container_resultado.winfo_children():
            children.destroy()

    def desenhar_resultado(self, matriz):
        converter_valor = self.CONVERSORES_MODO[self.modo_selecionado.get()]
        for linha in range(len(matriz)):
            for coluna in range(len(matriz[0])):
                valor_convertido = matriz[linha][coluna]
                valor_convertido = converter_valor(valor_convertido)
                resultado = tk.Label(self.container_resultado, text=str(valor_convertido), borderwidth=1, relief="sunken", width=7)
                resultado.grid(row=linha, column=coluna, padx=1, pady=1)
        
    def obter_valor_matriz(self):
        matriz = []
        try:
            for linha in range(self.numero_linhas.get()):
                valores_linha = []
                for coluna in range(self.numero_colunas.get()):
                    valor = int(self.container_matriz.grid_slaves(row=linha, column=coluna)[0].get())
                    valores_linha.append(valor)
                matriz.append(valores_linha)
            return matriz
        except:
            messagebox.showerror("Erro", self.ERRO_OBTER_VALOR_MATRIZ)
            return None

    def realizar_escalonamento_automatico(self):
        matriz = self.obter_valor_matriz()
        if matriz:
            transformador = MatrizCondensadaEscada(matriz)
            resultado = transformador.condensar()
            transformador.imprimir_matriz()
            self.limpar_resultado()
            self.desenhar_resultado(resultado)

    def realizar_escalonamento(self):
        matriz = self.obter_valor_matriz()
        if matriz:
            self.campo_numero_linhas.config(**self.ESTADO_DESABILITADO)
            self.campo_numero_colunas.config(**self.ESTADO_DESABILITADO)
            transformador = MatrizCondensadaEscada(matriz)
            resultado = transformador.condensar()
            transformador.imprimir_matriz()
            self.limpar_resultado()
            self.desenhar_resultado(resultado)
            self.limpar_btn.config(**self.ESTADO_NORMAL)

    def alterar_modo_saida(self):
        self.modo_selecionado_display.set(self.modos[self.modo_selecionado.get()])
        self.realizar_escalonamento_automatico()

    def randomizar(self):
        self.limpar()
        for linha in range(self.numero_linhas.get()):
            for coluna in range(self.numero_colunas.get()):
                numero = random.randint(-50, 50)
                numero = random.choice([numero, 0, 0])
                entry = self.container_matriz.grid_slaves(row=linha, column=coluna)[0]
                entry.delete(0, 'end')
                entry.insert(0, str(numero))

    def limpar(self):
        self.limpar_matriz()
        self.limpar_resultado()
        self.desenhar_matriz()
        self.campo_numero_linhas.config(**self.ESTADO_NORMAL)
        self.campo_numero_colunas.config(**self.ESTADO_NORMAL)
        self.limpar_btn.config(**self.ESTADO_DESABILITADO)




if __name__ == "__main__":
    janela = tk.Tk()
    janela.resizable(0, 0)
    janela.title(f"{Info.DISCIPLINA} - {Info.ALUNO} - {Info.PROJETO}")
    janela.geometry("590x360")
    janela.configure(borderwidth=8)
    Aplicacao(janela)
    Utils.centralizar_janela(janela)
    janela.mainloop()