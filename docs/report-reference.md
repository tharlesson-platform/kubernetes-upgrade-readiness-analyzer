# Referencia de relatorio

Este documento resume os campos gerados pela ferramenta e como eles podem ser interpretados por pessoas e pipelines.

## Estrutura do `report.json`

| Campo | Tipo | Significado |
| --- | --- | --- |
| `title` | string | Nome logico do relatório |
| `target_version` | string | Versao alvo informada na CLI |
| `source_version` | string ou null | Versão atual opcional |
| `readiness_score` | integer ou null | Score calculado a partir dos achados. Fica nulo sem manifests ou com snapshot de outro alvo |
| `upgrade_state` | string | `blocked` com blocker, `indeterminate` se faltam dados essenciais, `attention` com warnings ou `ready` para o escopo avaliado |
| `coverage` | objeto | Contagem de manifests e situação do snapshot de addons EKS |
| `blockers` | array | Findings impeditivos para um upgrade seguro |
| `warnings` | array | Findings de atencao que pedem ajuste ou validacao |
| `checklist` | array | Proximos passos operacionais sugeridos |

Cada item de `blockers` e `warnings` segue o mesmo formato:

| Campo | Tipo | Significado |
| --- | --- | --- |
| `resource` | string | Nome do recurso afetado |
| `reason` | string | Motivo do finding |
| `source` | string | Origem do arquivo que gerou o finding |

Achados de API removida incluem `api_version`, `removed_in` e `impact`. O impacto pode ser `removed_during_upgrade`, `already_unavailable_at_source` ou `unavailable_at_target` quando a origem é omitida.

`coverage.eks_addons` pode ser `matched`, `target_mismatch`, `unversioned` ou `missing`. `coverage.eks_addons_target_version` contém a versão declarada pelo snapshot quando fornecida.

## Exemplo resumido

```json
{
  "source_version": "1.31",
  "target_version": "1.32",
  "readiness_score": 75,
  "blockers": [
    {
      "resource": "example-read-only",
      "api_version": "flowcontrol.apiserver.k8s.io/v1beta3",
      "removed_in": "1.32",
      "impact": "removed_during_upgrade",
      "source": "fixtures/api-removal/flowschema.yaml"
    }
  ]
}
```

## Estrutura do `report.md`

O markdown gerado organiza a leitura em quatro blocos:

1. cabeçalho com versões e cobertura
2. score consolidado
3. lista de blockers e warnings
4. checklist final

Esse formato funciona bem para:

- anexar em tickets de upgrade
- compartilhar em Slack ou wiki interna
- registrar a decisao de go/no-go da janela

## Como interpretar o score

Formula atual:

```text
readiness_score = max(0, 100 - (25 x blockers) - (5 x warnings))
```

Implicacoes praticas:

- um unico blocker ja derruba o score para `75`
- quatro blockers levam o score a `0`
- warnings isolados nao deveriam ser ignorados, mas o peso deles e menor

## Uso em pipeline

Padroes simples de automacao que combinam bem com o formato atual:

- usar `--fail-on-blockers` para obter código `1` com blockers e `2` sem manifests ou com snapshot de outro alvo, quando não há blocker comprovado
- sinalizar aprovacao manual se `warnings` for maior que zero
- armazenar `report.json` como artefato de build
- publicar `report.md` no sumario do pipeline

## Limites do modelo atual

- o relatório ainda nao agrega findings por namespace ou aplicacao
- o score reflete os manifests e os dados locais. Consulte `coverage` para identificar ausência de confirmação dos addons na versão-alvo
- o formato markdown ainda nao inclui links, tabelas ou anotacoes de linha

## Leitura complementar

- [README.md](../README.md)
- [docs/architecture.md](architecture.md)
- [docs/roadmap.md](roadmap.md)
