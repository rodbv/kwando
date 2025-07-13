[![Tests](https://github.com/rodbv/kwando/actions/workflows/test.yml/badge.svg)](https://github.com/rodbv/kwando/actions/workflows/test.yml)

# KWANDO: Dashboard de Simulação Monte Carlo

Dashboard para prever a conclusão de itens de trabalho usando simulações Monte Carlo. Feito com Python e [Panel](https://panel.holoviz.org/).

## Começando

### Pré-requisitos

- Python 3.12 ou superior
- Gerenciador de pacotes [uv](https://docs.astral.sh/uv/getting-started/installation/)

### Instalação

1. Instale o uv:
   ```sh
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Clone o repositório:
   ```sh
   git clone https://github.com/rodbv/kwando.git
   cd kwando
   ```

3. Instale as dependências:
   ```sh
   uv sync
   ```

4. Execute o dashboard:
   ```sh
   uv run panel serve src/dashboard.py
   ```

5. Abra seu navegador no URL mostrado no terminal (tipicamente `http://localhost:5006`)

## Formato dos Dados

Seu arquivo CSV deve conter pelo menos uma coluna `cycle_time_days` com valores numéricos positivos representando o tempo necessário para concluir itens de trabalho.

**Colunas obrigatórias:**
- `cycle_time_days`: Número de dias para concluir cada item de trabalho

**Colunas opcionais:**
- `tags`: Tags separadas por vírgula para filtragem (ex: "bug,frontend,alta-prioridade")

## Como Usar

1. **Carregar Dados**: Use a seção "Fonte de Dados" para carregar seu arquivo CSV ou escolher arquivos existentes
2. **Escolher Análise**:
   - **"Quando será concluído?"**: Calcular data de conclusão para um número específico de itens
   - **"Quantos itens?"**: Calcular quantos itens podem ser concluídos em um período
3. **Ajustar Parâmetros**: Definir número de itens ou período de datas
4. **Ver Resultados**: Ver percentis e níveis de confiança da previsão

## Desenvolvimento

### Configuração

1. Instale as dependências de desenvolvimento:
   ```sh
   uv sync --extra dev
   ```

2. Instale os hooks do pre-commit:
   ```sh
   uv run pre-commit install
   ```

3. Execute os testes:
   ```sh
   uv run pytest
   ```

### Qualidade do Código

O projeto usa:
- **Ruff** para linting e formatação
- **Pre-commit** hooks para verificações automatizadas
- **Pytest** para testes

Execute verificações de qualidade:
```sh
uv run ruff check .
uv run ruff format .
```

### Comandos com just

Este projeto usa o [just](https://github.com/casey/just) para simplificar comandos comuns de desenvolvimento.

#### Instalação do just

No macOS (Homebrew):
```sh
brew install just
```
No Linux:
```sh
sudo snap install --edge --classic just
```
Ou veja outras opções na [documentação oficial](https://github.com/casey/just#installation).

#### Exemplos de uso

- Rodar o dashboard:
  ```sh
  just run
  ```
- Rodar os testes (uma vez):
  ```sh
  just test
  ```
- Rodar os testes em modo watch (auto-reload):
  ```
