# Guia de reproducao

Este guia ajuda novos colaboradores a entender rapidamente o que a ferramenta considera blocker e warning de upgrade.

## Pre-requisitos

- Python 3.11+
- dependencias instaladas com `python -m pip install -e .[dev]`

## Primeira execucao recomendada

```bash
kubernetes-upgrade-readiness-analyzer scan --manifests-path fixtures/problematic --target-version 1.29 --output-dir artifacts/1.29
```

Depois confira:

- `artifacts/1.29/report.json`
- `artifacts/1.29/report.md`

## Segunda execucao recomendada

```bash
kubernetes-upgrade-readiness-analyzer scan --manifests-path fixtures/problematic --target-version 1.30 --output-dir artifacts/1.30
```

Esse segundo passo ajuda a ver como o risco muda entre versoes alvo diferentes.

## O que revisar na saida

- `readiness_score`
- `blockers`
- `warnings`
- recomendações e checklist final

## Erros comuns

- Apontar para manifests nao renderizados quando o time usa Helm e esperar uma leitura completa.
- Misturar arquivos de varios ambientes no mesmo diretorio de teste.
- Avaliar uma versao alvo sem saber qual e a versao atual do cluster.

## Fluxo recomendado para onboarding

1. Rodar o fixture problematico
2. Ler o markdown
3. Testar outra `target-version`
4. Depois apontar para um diretorio real do time
