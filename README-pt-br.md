[🇬🇧 English](README.md) | [🇧🇷 Português](README-pt-br.md)

[![Tests](https://github.com/rodbv/kwando/actions/workflows/test.yml/badge.svg)](https://github.com/rodbv/kwando/actions/workflows/test.yml)
![Coverage](https://img.shields.io/badge/coverage-97%25-green)

# KWANDO: Dashboard de Simulação Monte Carlo

Dashboard para prever a conclusão de itens de trabalho usando simulações Monte Carlo. Feito com Python e [Panel](https://panel.holoviz.org/).

<img src="docs/images/screencap.gif" alt="KWANDO Dashboard Screenshot" style="max-width: 600px; box-shadow: 0 4px 24px #0003; border-radius: 8px; margin: 1em 0;" />

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

---

## Contribuindo

Contribuições são bem-vindas! Veja o [Guia de Contribuição](CONTRIBUTING.md) para detalhes sobre como enviar issues, sugestões e pull requests.

## Código de Conduta

Este projeto segue um [Código de Conduta](CODE_OF_CONDUCT.md). Ao participar, espera-se que você siga este código.

## Licença

Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Créditos

- Simulação Monte Carlo adaptada de [rueedlinger/monte-carlo-simulation](https://github.com/rueedlinger/monte-carlo-simulation)
- Inspirado no livro [Actionable Agile Metrics for Predictability: An Introduction](https://actionableagile.com/books/aamfp/) de Daniel Vacanti
