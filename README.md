# Kubernetes Upgrade Readiness Analyzer

CLI para avaliar se manifests e clusters estão prontos para upgrade Kubernetes/EKS.

## Problema que resolve

- Upgrades Kubernetes/EKS falham quando APIs deprecated e addons incompatíveis passam despercebidos.
- Times precisam de uma checklist objetiva antes da janela de manutenção.
- A ferramenta destaca blockers, warnings e um score de readiness por pasta de manifests.

## Arquitetura

- Scanners carregam YAML puro ou Helm renderizado.
- Regras mapeiam versões deprecated e padrões incompatíveis.
- Reports entregam markdown/json simples para pipeline ou validação manual.

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

## Exemplos reais

- `kubernetes-upgrade-readiness-analyzer scan --manifests-path fixtures/problematic --target-version 1.29`
- `kubernetes-upgrade-readiness-analyzer scan --manifests-path ./rendered --target-version 1.30`

## Como isso ajuda SREs no dia a dia

- Evita blockers surpresa no meio da janela de upgrade.
- Cria checklist reproduzível para times de plataforma e SRE.
- Ajuda a priorizar correções de manifests antigos por criticidade.

## Roadmap

- Matriz específica de addons EKS.
- Suporte a score por namespace e app.
- Gate automático em pipeline de upgrade.

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
