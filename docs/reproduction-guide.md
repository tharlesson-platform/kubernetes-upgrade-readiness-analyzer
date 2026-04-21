# Guia de reproducao

Este guia ajuda novos colaboradores a entender rapidamente o que a ferramenta considera blocker, warning e baseline saudavel para upgrade.

## Objetivo da reproducao

Ao final deste passo a passo, a pessoa deve conseguir:

- entender o que entra como blocker e warning
- interpretar o `readiness_score`
- comparar um cenário com risco alto e um cenário pronto
- saber o que ainda e limitacao atual do projeto

## Pre-requisitos

- Python 3.11+
- dependencias instaladas com `python -m pip install -e .[dev]`

## Cenarios disponiveis

| Cenario | Caminho | Resultado esperado |
| --- | --- | --- |
| Problematico | `fixtures/problematic` | 4 blockers, 1 warning e score 0 |
| Saudavel | `fixtures/ready` | 0 blockers, 0 warnings e score 100 |

## Primeira execucao recomendada

```bash
kubernetes-upgrade-readiness-analyzer scan --manifests-path fixtures/problematic --target-version 1.29 --output-dir artifacts/1.29
```

Depois confira:

- `artifacts/1.29/report.json`
- `artifacts/1.29/report.md`

O que voce deve encontrar nesse cenário:

- 3 blockers vindos de `legacy.yaml`
- 1 blocker vindo de `eks-addons.json`
- 1 warning vindo de `eks-addons.json`
- score final `0`

## Segunda execucao recomendada

```bash
kubernetes-upgrade-readiness-analyzer scan --manifests-path fixtures/problematic --target-version 1.30 --output-dir artifacts/1.30
```

Leitura importante:

- hoje o campo `target_version` muda no relatório
- a matriz de regras ainda nao e version-aware
- por isso, neste estado atual do projeto, `1.29` e `1.30` devem produzir os mesmos findings para o mesmo fixture

## Terceira execucao recomendada

```bash
kubernetes-upgrade-readiness-analyzer scan --manifests-path fixtures/ready --target-version 1.29 --output-dir artifacts/ready-1.29
```

Esse passo mostra a baseline minima esperada:

- nenhum blocker
- nenhum warning
- score `100`

## Tabela de resultados esperados

| Comando | Blockers | Warnings | Score | Observacao |
| --- | ---: | ---: | ---: | --- |
| `fixtures/problematic` `1.29` | 4 | 1 | 0 | Ambiente claramente nao pronto |
| `fixtures/problematic` `1.30` | 4 | 1 | 0 | Mesmo resultado, porque as regras ainda nao variam por versao |
| `fixtures/ready` `1.29` | 0 | 0 | 100 | Baseline saudavel para o conjunto atual de regras |

## O que revisar na saida

### `readiness_score`

- score sintetico para triagem inicial
- nao substitui leitura detalhada de blockers e warnings

### `blockers`

- itens que deveriam impedir a janela ate serem corrigidos
- neste repositorio, cada blocker reduz 25 pontos do score

### `warnings`

- itens que merecem ajuste ou confirmacao antes do upgrade
- cada warning reduz 5 pontos do score

### `checklist`

- resumo operacional do que revisar antes da reexecucao

## Perguntas que o time deve responder apos a reproducao

- quais findings sao apenas do fixture e quais refletem problemas reais do ambiente?
- os manifests do time sao YAML puros ou Helm renderizado?
- o snapshot de addons EKS que sera usado na analise esta atualizado?
- o time precisa de score global ou de score por namespace/app?

## Erros comuns

- Apontar para manifests nao renderizados quando o time usa Helm e esperar uma leitura completa.
- Misturar arquivos de varios ambientes no mesmo diretorio de teste.
- Avaliar uma versao alvo sem saber qual e a versao atual do cluster.
- Assumir que `target_version` ja muda automaticamente o catalogo de regras.

## Fluxo recomendado para onboarding

1. Rodar o fixture problematico.
2. Ler `report.md`.
3. Comparar com `fixtures/ready`.
4. Testar outra `target-version`.
5. Depois apontar para um diretório real do time.
