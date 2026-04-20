# Kubernetes Upgrade Readiness Analyzer Architecture

## Visão geral

Scanner de manifests YAML/Helm renderizado para medir readiness antes de upgrades Kubernetes/EKS.

## Fluxo

- Scanners carregam todos os documentos YAML do diretório alvo.
- Regras mapeiam APIs deprecated e padrões incompatíveis por versão.
- O relatório final separa blockers, warnings e score de readiness.

## Extensões futuras

- Incluir matriz de versões específicas de addons EKS.
- Analisar CRDs customizadas com regras por vendor.
- Emitir anotação automática em pipeline.
