# Projeto TR1
Esse é o projeto da matéria Teleinfomática e Redes 1, ministrada pelo professor Marcelo Antonio Marotta. Trata-se de uma simulação das camadas física e de enlace do modelo OSI, apresentada por uma interface gráfica (GUI). O projeto foi todo desenvolvido em C++. A arquitetura do projeto é como segue:
## Estrutura de Diretórios

```plaintext
Projeto-CamadaFisicaEnlace/
|-- include/
|   |-- headers
|
|-- src/
|   |-- camada_fisica/
|   |   |-- aquivos .cpp referentes à camada física
|   |
|   |-- camada_enlace/
|   |   |-- aquivos .cpp referentes à camada de enlace
|
|-- gui/
|   |-- arquivos da interface gráfica
|
|-- assets/
|   |-- rescursos da interface gráfica
|
```

## Descrição dos Diretórios

### `include/`
Contém os arquivos de cabeçalho (.h) com as declarações das classes e funções utilizadas no projeto.

- **Transmissor.h**: Declarações relacionadas à classe `Transmissor` (modulações digitais e por portadora).
- **Receptor.h**: Declarações relacionadas à classe `Receptor` (demodulações).

### `src/`
Contém os arquivos de implementação (.cpp) das classes e funções declaradas nos cabeçalhos.

- **Transmissor.cpp**: Implementação das funções de modulação digital e por portadora.
- **Receptor.cpp**: Implementação das funções de demodulação digital e por portadora.
- **main.cpp**: Ponto de entrada do programa.

### `gui/`
Arquivos relacionados à interface gráfica do usuário (GUI).

### `assets/`
Contém recursos estáticos para a interface, como ícones, folhas de estilo ou imagens.

- **icons/**: ícones usados na GUI.
- **styles/**: Folhas de estilo ou arquivos de configuração da interface.
