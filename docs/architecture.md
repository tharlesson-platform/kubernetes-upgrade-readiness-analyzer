# Kubernetes Upgrade Readiness Analyzer Architecture

## Visao geral

Scanner de manifests YAML e snapshots de addons EKS para medir readiness antes de upgrades Kubernetes/EKS.

O objetivo da arquitetura atual e manter o fluxo simples:

- leitura local de dados
- avaliacao deterministica de regras
- saida em formatos legiveis por humanos e por automacao

## Componentes

- `cli/main.py`
  - expõe os comandos `scan` e `version`
  - coordena leitura, avaliacao e escrita dos artefatos
- `scanners/manifests.py`
  - percorre o diretório informado
  - carrega todos os arquivos `*.yaml` e `*.yml`
  - anexa `_source` em cada documento para rastreabilidade
- `scanners/addons.py`
  - procura `eks-addons.json` no mesmo diretório avaliado
  - carrega o snapshot de addons quando ele existe
- `rules/catalog.py`
  - concentra as regras de manifests
  - calcula blockers, warnings e score final
- `rules/addons.py`
  - transforma status de addons em findings operacionais
- `reports/renderers.py`
  - renderiza a versao markdown do relatório

## Fluxo detalhado

1. O operador chama `kubernetes-upgrade-readiness-analyzer scan`.
2. A CLI resolve `manifests_path`, `target_version` e `output_dir`.
3. O scanner de manifests percorre YAMLs do diretório.
4. O scanner de addons tenta abrir `eks-addons.json`.
5. O catalogo aplica regras estaticas sobre os documentos carregados.
6. A avaliacao de addons classifica cada item como blocker, warning ou neutro.
7. O score de readiness e calculado.
8. O resultado final e gravado em `report.json` e `report.md`.

## Entradas suportadas hoje

### Manifests

- YAML puro
- Helm ja renderizado
- multiplos documentos no mesmo arquivo

### Addons

- arquivo local `eks-addons.json`
- estrutura esperada:

```json
[
  { "name": "vpc-cni", "status": "upgrade-required" },
  { "name": "aws-ebs-csi-driver", "status": "unsupported" }
]
```

## Regras ativas no catalogo atual

| Categoria | Regra | Severidade | Motivo operacional |
| --- | --- | --- | --- |
| API removida | `extensions/v1beta1` `Ingress` | Blocker | Deve migrar para `networking.k8s.io/v1` |
| API removida | `networking.k8s.io/v1beta1` `Ingress` | Blocker | Deve migrar para `networking.k8s.io/v1` |
| API removida | `policy/v1beta1` `PodSecurityPolicy` | Blocker | PSP foi removido |
| API removida | `apiextensions.k8s.io/v1beta1` `CustomResourceDefinition` | Blocker | CRD precisa ser promovida para `v1` |
| Qualidade minima | `Ingress` `v1` sem `ingressClassName` | Warning | Risco de comportamento ambiguo no controlador |
| Qualidade minima | `Deployment` sem label de pod security | Warning | Indica preparo incompleto para politicas modernas |
| Qualidade minima | `CRD` `v1` sem `spec.versions` | Warning | Estrutura incompleta para API `v1` |
| Addon EKS | `status=unsupported` | Blocker | Addon nao suporta a versao alvo pretendida |
| Addon EKS | `status=upgrade-required` | Warning | Upgrade do addon deve ocorrer antes do cluster |

## Score e saidas

O score atual prioriza simplicidade de leitura:

```text
readiness_score = max(0, 100 - (25 x blockers) - (5 x warnings))
```

Saidas produzidas:

- `report.json`
  - indicado para automacoes, CI e parse por outras ferramentas
- `report.md`
  - indicado para review humano e checklist operacional

## Baseline dos fixtures incluidos

| Fixture | Blockers | Warnings | Score | Leitura |
| --- | ---: | ---: | ---: | --- |
| `fixtures/problematic` | 4 | 1 | 0 | Exemplo de ambiente claramente nao pronto para upgrade |
| `fixtures/ready` | 0 | 0 | 100 | Exemplo de baseline minima saudavel para o conjunto atual de regras |

## Limitacoes atuais

- `target_version` ainda nao altera a matriz de regras; hoje ele funciona como contexto do relatório.
- A analise de addons depende do snapshot fornecido localmente.
- O score e agregado por diretório, sem agregacao por namespace, app ou ambiente.
- Nao ha anotacao nativa em PR, SARIF ou comentario em CI.

## Pontos de extensao

- Tornar o catalogo de regras version-aware por release Kubernetes.
- Adicionar matriz mais rica para addons EKS.
- Agrupar findings por namespace, app, equipe ou tenant.
- Emitir formatos extras de relatorio para pipeline e observabilidade.

## Leitura complementar

- [docs/reproduction-guide.md](reproduction-guide.md)
- [docs/report-reference.md](report-reference.md)
- [docs/roadmap.md](roadmap.md)
