# Examples

Os exemplos principais deste repositorio ficam em `fixtures/problematic`, porque representam manifests e addons usados diretamente pelos testes e pela demonstracao da CLI.

## Ordem recomendada

1. Rode a ferramenta em `fixtures/problematic`
2. Leia `artifacts/report.md`
3. So depois aponte para manifests renderizados do seu time

## Cenario principal

- `fixtures/problematic/legacy.yaml`
  - Manifest com APIs antigas e sinais de incompatibilidade.

- `fixtures/problematic/eks-addons.json`
  - Snapshot simples de addons EKS para complementar a analise.

## Comandos recomendados

```bash
kubernetes-upgrade-readiness-analyzer scan --manifests-path fixtures/problematic --target-version 1.29 --output-dir artifacts/1.29
```

```bash
kubernetes-upgrade-readiness-analyzer scan --manifests-path fixtures/problematic --target-version 1.30 --output-dir artifacts/1.30
```

## Saidas esperadas

- `report.json`
- `report.md`
