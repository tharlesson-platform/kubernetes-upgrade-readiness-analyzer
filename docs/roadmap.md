# Roadmap

Este roadmap transforma a visao inicial do projeto em um plano mais concreto de evolucao tecnica, operacional e documental.

## Objetivo do produto

O `kubernetes-upgrade-readiness-analyzer` deve responder, de forma simples e auditavel, a pergunta:

> este conjunto de manifests e addons esta pronto para seguir para um upgrade Kubernetes/EKS?

Para isso, a ferramenta precisa equilibrar:

- cobertura tecnica suficiente para detectar riscos reais
- saida facil de explicar para SRE, plataforma e aplicacoes
- integracao simples com fluxo manual e pipeline

## Baseline atual

Hoje o projeto entrega:

- leitura local de YAML e `eks-addons.json`
- deteccao de APIs removidas conhecidas
- warnings basicos de `Ingress`, `Deployment` e `CRD`
- score simples por diretório
- saida em `report.json` e `report.md`

Dados de referencia dos fixtures incluidos:

| Fixture | Blockers | Warnings | Score | O que representa |
| --- | ---: | ---: | ---: | --- |
| `fixtures/problematic` | 4 | 1 | 0 | Ambiente que deveria impedir a janela |
| `fixtures/ready` | 0 | 0 | 100 | Baseline minima limpa |

## Principios do roadmap

- Priorizar sinais que realmente mudam decisao operacional.
- Evitar complexidade antes de consolidar o fluxo basico.
- Expandir documentacao e exemplos junto com cada nova capacidade.
- Manter output legivel para humanos e automatizavel por maquinas.

## Fase 1 - Cobertura e confianca

Objetivo:

- tornar a analise mais fiel a upgrades reais sem perder simplicidade

Entregaveis:

- catalogo version-aware por versao alvo Kubernetes
- matriz mais rica de addons EKS por versao suportada
- findings com severidade, categoria e sugestao de remediacao
- comparativo mais claro entre findings de manifests e de addons
- documentacao com tabelas de compatibilidade e exemplos adicionais

Valor esperado:

- menos ambiguidade ao usar `target_version`
- mais confianca para decidir ordem de upgrade entre cluster e addons

## Fase 2 - Adoção operacional

Objetivo:

- levar a ferramenta do uso local para o fluxo recorrente do time

Entregaveis:

- score por namespace, app ou unidade de deploy
- suporte a allowlist ou suppressions justificadas
- gate automatico em pipeline de upgrade
- saidas extras para CI, como anotacoes e formatos mais estruturados
- exemplos de integracao com pull request, changelog e checklist de janela

Valor esperado:

- priorizacao melhor entre equipes
- menos retrabalho na aprovacao da mudanca
- maior reaproveitamento do relatório entre engenharia e operacao

## Fase 3 - Inteligencia operacional

Objetivo:

- transformar readiness em um sinal continuo, nao apenas pontual

Entregaveis:

- ingestao opcional de dados do cluster real
- regras para CRDs customizadas por vendor ou plataforma interna
- historico de scans e tendencia de readiness ao longo do tempo
- score com mais contexto, incluindo regressao entre execucoes
- playbooks de remediacao por tipo de finding

Valor esperado:

- deteccao antecipada de regressao
- preparo continuo para upgrades, sem depender apenas da janela

## Fase documental permanente

Esses itens devem crescer junto com todas as fases acima:

- exemplos positivos e negativos por cenário
- guia de reproducao sempre sincronizado com os fixtures
- referencia de campos do relatório
- tabela de limitacoes conhecidas e decisoes de design

## Fora de escopo por enquanto

- consulta online automatica a fontes externas de compatibilidade
- correcoes automaticas de manifests
- analise generica de qualquer tipo de recurso de cluster sem regra explicita

## Definicao de pronto para cada fase

Uma fase so deve ser considerada concluida quando houver:

- regra implementada e testada
- exemplo reproduzivel no repositorio
- documentacao explicando comportamento esperado
- criterio operacional claro de como usar a nova capacidade

## Proximo passo recomendado

Se o objetivo for entregar mais valor rapido, a melhor sequencia e:

1. tornar `target_version` realmente determinante no catalogo
2. enriquecer a matriz de addons EKS
3. adicionar score por namespace/app
4. publicar gate automatizado de pipeline
