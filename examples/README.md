# Examples

Os exemplos principais deste repositorio ficam em `fixtures/`, porque representam os cenarios usados nos testes, na demonstracao da CLI e no onboarding rapido.

## Ordem recomendada

1. Rode a ferramenta em `fixtures/problematic`.
2. Leia `report.md` e identifique blockers e warnings.
3. Rode a ferramenta em `fixtures/ready`.
4. Compare os dois resultados antes de analisar manifests reais.

## Fixtures disponiveis

| Fixture | Objetivo | Resultado esperado |
| --- | --- | --- |
| `fixtures/problematic` | Mostrar falhas classicas de readiness | 4 blockers, 1 warning e score 0 |
| `fixtures/ready` | Mostrar a baseline minima saudavel | 0 blockers, 0 warnings e score 100 |

## Cenario problematico

Arquivos:

- `fixtures/problematic/legacy.yaml`
  - `Ingress` em `extensions/v1beta1`
  - `PodSecurityPolicy` em `policy/v1beta1`
  - `CustomResourceDefinition` em `apiextensions.k8s.io/v1beta1`
- `fixtures/problematic/eks-addons.json`
  - `vpc-cni` com status `upgrade-required`
  - `aws-ebs-csi-driver` com status `unsupported`

Leitura operacional:

- exemplifica o tipo de diretório que deveria bloquear uma janela de upgrade
- ajuda a explicar por que addons e manifests precisam ser avaliados juntos

## Cenario saudavel

Arquivos:

- `fixtures/ready/platform.yaml`
  - `Ingress` ja em `networking.k8s.io/v1` com `ingressClassName`
  - `Deployment` com label `pod-security.kubernetes.io/enforce`
  - `CRD` em `apiextensions.k8s.io/v1` com `spec.versions`
- `fixtures/ready/eks-addons.json`
  - addons marcados como `supported`

Leitura operacional:

- serve como contraste direto com o cenário problematico
- mostra como a ferramenta se comporta quando a baseline minima esta limpa

## Comandos recomendados

```bash
kubernetes-upgrade-readiness-analyzer scan --manifests-path fixtures/problematic --target-version 1.29 --output-dir artifacts/1.29
```

```bash
kubernetes-upgrade-readiness-analyzer scan --manifests-path fixtures/problematic --target-version 1.30 --output-dir artifacts/1.30
```

```bash
kubernetes-upgrade-readiness-analyzer scan --manifests-path fixtures/ready --target-version 1.29 --output-dir artifacts/ready-1.29
```

## O que comparar entre as saidas

| Campo | `problematic` | `ready` | O que isso ensina |
| --- | --- | --- | --- |
| `readiness_score` | `0` | `100` | O peso relativo de blockers e warnings |
| `blockers` | APIs removidas e addon sem suporte | vazio | O que realmente deveria travar a mudanca |
| `warnings` | addon com upgrade previo | vazio | O que precisa de ajuste, mas nao e impeditivo isoladamente |
| `checklist` | presente | presente | O relatório sempre orienta o proximo passo |

## Saidas esperadas

- `report.json`
- `report.md`

Para uma leitura guiada mais detalhada, consulte [docs/reproduction-guide.md](../docs/reproduction-guide.md).
