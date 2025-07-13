[![Tests](https://github.com/rodbv/kwando/actions/workflows/test.yml/badge.svg)](https://github.com/rodbv/kwando/actions/workflows/test.yml)

# KWANDO: Dashboard de Simulação Monte Carlo

Dashboard para prever a conclusão de itens de trabalho usando simulações Monte Carlo. Feito com Python e [Panel](https://panel.holoviz.org/).

<img width="1435" height="759" alt="image" src="https://github.com/user-attachments/assets/62971b26-4dd1-45fd-b679-859f5d79d3a0" />


## Funcionalidades

- **Prever Datas de Conclusão**: Calcular quando um número específico de itens será concluído
- **Planejamento de Capacidade**: Calcular quantos itens podem ser concluídos em um período
- **Upload de Dados**: Usar seus próprios arquivos CSV ou dados de exemplo
- **Filtros por Tags**: Filtrar análise por tags de itens de trabalho
- **Interface Web**: Dashboard com cálculos em tempo real
- **Percentis**: Visualizar percentis (70%, 80%, 90%, 95%, 98%) para níveis de confiança

## O que é Simulação Monte Carlo?

A simulação Monte Carlo usa dados históricos de tempo de ciclo para executar milhares de simulações. Em vez de uma estimativa única, você obtém previsões com diferentes níveis de confiança, considerando a variabilidade natural dos tempos de conclusão.

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
   git clone https://github.com/seu-usuario/kwando.git
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
  ```sh
  just test-watch
  ```
- Checar qualidade do código:
  ```sh
  just lint
  just format
  ```
- Ver todos os comandos disponíveis:
  ```sh
  just --list
  ```

## Contribuindo

Contribuições são bem-vindas! Veja o [Guia de Contribuição](CONTRIBUTING.md) para detalhes sobre como enviar issues, solicitações de recursos e pull requests.

## Código de Conduta

Este projeto segue um [Código de Conduta](CODE_OF_CONDUCT.md). Ao participar, você deve seguir este código.

## Licença

Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Créditos

- Simulação Monte Carlo adaptada de [rueedlinger/monte-carlo-simulation](https://github.com/rueedlinger/monte-carlo-simulation)
- Teoria baseada no [ActionableAgile](https://www.actionableagile.com/) de Daniel Vacanti

---

**English**: [README-en.md](README-en.md)
