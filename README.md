# Kubernetes Upgrade Readiness Analyzer

CLI para avaliar se manifests e snapshots de addons estao prontos para upgrade Kubernetes/EKS.

## Resumo executivo

- Detecta blockers comuns antes da janela de upgrade, como APIs removidas e addons sem suporte.
- Gera `report.json` e `report.md` para uso manual, pipeline ou handoff entre SRE e plataforma.
- Fornece uma baseline simples de readiness por diretório de manifests.
- Inclui exemplos de cenarios com falhas e de cenarios saudaveis para acelerar onboarding.

## Problema que resolve

- Upgrades Kubernetes/EKS falham quando APIs deprecated e addons incompatíveis passam despercebidos.
- Times precisam de uma checklist objetiva antes da janela de manutenção.
- A ferramenta destaca blockers, warnings e um score de readiness por pasta de manifests.

## O que a ferramenta verifica hoje

- APIs removidas ou deprecated em manifests:
  - `extensions/v1beta1` `Ingress`
  - `networking.k8s.io/v1beta1` `Ingress`
  - `policy/v1beta1` `PodSecurityPolicy`
  - `apiextensions.k8s.io/v1beta1` `CustomResourceDefinition`
- Qualidade minima em recursos ja migrados:
  - `Ingress` `networking.k8s.io/v1` sem `ingressClassName`
  - `Deployment` sem label `pod-security.kubernetes.io/enforce`
  - `CustomResourceDefinition` `v1` sem bloco `spec.versions`
- Snapshot de addons EKS em `eks-addons.json`:
  - `unsupported` vira blocker
  - `upgrade-required` vira warning

## Arquitetura

- Scanners carregam YAML puro ou Helm renderizado a partir do filesystem local.
- Regras mapeiam versões deprecated e padrões incompatíveis.
- Reports entregam markdown/json simples para pipeline ou validação manual.

Mais detalhes em:

- [docs/architecture.md](docs/architecture.md)
- [docs/report-reference.md](docs/report-reference.md)

## Estrutura do projeto

```text
.
|-- cli/
|-- scanners/
|-- rules/
|-- reports/
|-- fixtures/
|-- tests/
|-- docs/
|-- pyproject.toml
|-- Makefile
|-- .github/workflows/ci.yml
|-- README.md
|-- LICENSE
|-- NOTICE
```

## Como executar

```bash
python -m pip install -e .[dev]
kubernetes-upgrade-readiness-analyzer scan --manifests-path fixtures/problematic --target-version 1.29
```

## Fluxo recomendado de uso

1. Rode o cenário com falhas em `fixtures/problematic`.
2. Compare com o cenário saudavel em `fixtures/ready`.
3. Revise `report.json` e `report.md` para entender score, blockers e warnings.
4. Aplique a mesma sequencia em manifests renderizados do time.

## Cenarios incluidos no repositorio

| Cenario | Caminho | Blockers esperados | Warnings esperados | Score esperado | Objetivo |
| --- | --- | ---: | ---: | ---: | --- |
| Problematico | `fixtures/problematic` | 4 | 1 | 0 | Demonstrar APIs removidas, CRD antiga e addons EKS com risco |
| Saudavel | `fixtures/ready` | 0 | 0 | 100 | Mostrar a baseline minima esperada depois da correcao |

## Como interpretar o score

O score atual usa uma formula simples para facilitar triagem:

```text
readiness_score = max(0, 100 - (25 x blockers) - (5 x warnings))
```

Leitura sugerida:

- `100`: baseline limpa para o conjunto de regras atual.
- `95` a `75`: sem blockers, mas com warnings que merecem ajuste antes da mudança.
- `70` ou menos: o ambiente pede analise cuidadosa.
- `0`: existe uma combinacao de blockers suficiente para impedir um upgrade seguro.

## Saidas geradas

- `report.json`: formato mais facil para integrações, parse em CI ou armazenamento.
- `report.md`: formato de leitura humana para checklist, review e registro da janela.

Cada finding traz:

- `resource`
- `reason`
- `source`

## Reproducao guiada

Comandos recomendados:

```bash
kubernetes-upgrade-readiness-analyzer scan --manifests-path fixtures/problematic --target-version 1.29 --output-dir artifacts/1.29
kubernetes-upgrade-readiness-analyzer scan --manifests-path fixtures/problematic --target-version 1.30 --output-dir artifacts/1.30
kubernetes-upgrade-readiness-analyzer scan --manifests-path fixtures/ready --target-version 1.29 --output-dir artifacts/ready-1.29
```

Para onboarding mais rapido:

- consulte [examples/README.md](examples/README.md)
- siga [docs/reproduction-guide.md](docs/reproduction-guide.md)

## Exemplos reais

- `kubernetes-upgrade-readiness-analyzer scan --manifests-path fixtures/problematic --target-version 1.29`
- `kubernetes-upgrade-readiness-analyzer scan --manifests-path fixtures/ready --target-version 1.29`
- `kubernetes-upgrade-readiness-analyzer scan --manifests-path ./rendered --target-version 1.30`

## Como isso ajuda SREs no dia a dia

- Evita blockers surpresa no meio da janela de upgrade.
- Cria checklist reproduzível para times de plataforma e SRE.
- Ajuda a priorizar correções de manifests antigos por criticidade.
- Facilita handoff entre quem prepara manifests e quem aprova a mudança.
- Entrega resumo visual por severidade e kind, com HTML pronto para compartilhamento.

## Limitacoes atuais

- `target_version` ainda aparece no relatório, mas o catalogo de regras ainda nao muda por versao alvo.
- A analise de addons depende do snapshot local `eks-addons.json`, sem consulta externa.
- O scanner espera manifests YAML ou Helm ja renderizado.
- O score atual e global por diretório, sem agrupamento por namespace, app ou tenant.

## Documentacao complementar

- [docs/architecture.md](docs/architecture.md): componentes, fluxo e pontos de extensao.
- [docs/reproduction-guide.md](docs/reproduction-guide.md): passo a passo para rodar e interpretar os cenarios.
- [docs/report-reference.md](docs/report-reference.md): referencia de campos e uso em pipeline.
- [docs/roadmap.md](docs/roadmap.md): roadmap expandido com fases, entregaveis e criterios.
- [examples/README.md](examples/README.md): leitura orientada dos fixtures inclusos.

## Roadmap

Roadmap detalhado: [docs/roadmap.md](docs/roadmap.md)

- Fase 1: tornar o catalogo version-aware e enriquecer a matriz de addons EKS.
- Fase 2: adicionar score por namespace/app e gates automatizados em pipeline.
- Fase 3: expandir ingestao de dados de cluster, CRDs customizadas e historico de readiness.

## Licença

Este projeto está licenciado sob a Apache License 2.0. Consulte o arquivo `LICENSE` para mais detalhes.

## Atribuição

Este projeto foi desenvolvido e publicado por **Tharlesson**.
Caso você utilize este material como base em ambientes internos, estudos, adaptações ou redistribuições, preserve os créditos de autoria e os avisos de licença aplicáveis.

## Créditos e Uso

Este repositório foi criado com foco em automação, padronização operacional e melhoria da rotina de profissionais de SRE, DevOps, Cloud e Plataforma.

Você pode:

- estudar
- reutilizar
- adaptar
- evoluir este projeto dentro do seu contexto

Ao reutilizar ou derivar este material:

- mantenha os avisos de licença
- preserve os créditos de autoria quando aplicável
- documente alterações relevantes feitas sobre a base original

## Autor

**Tharlesson**  
GitHub: https://github.com/tharlesson
