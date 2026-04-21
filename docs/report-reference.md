# Referencia de relatorio

Este documento resume os campos gerados pela ferramenta e como eles podem ser interpretados por pessoas e pipelines.

## Estrutura do `report.json`

| Campo | Tipo | Significado |
| --- | --- | --- |
| `title` | string | Nome logico do relatório |
| `target_version` | string | Versao alvo informada na CLI |
| `readiness_score` | integer | Score sintetico calculado a partir de blockers e warnings |
| `blockers` | array | Findings impeditivos para um upgrade seguro |
| `warnings` | array | Findings de atencao que pedem ajuste ou validacao |
| `checklist` | array | Proximos passos operacionais sugeridos |

Cada item de `blockers` e `warnings` segue o mesmo formato:

| Campo | Tipo | Significado |
| --- | --- | --- |
| `resource` | string | Nome do recurso afetado |
| `reason` | string | Motivo do finding |
| `source` | string | Origem do arquivo que gerou o finding |

## Exemplo resumido

```json
{
  "target_version": "1.29",
  "readiness_score": 0,
  "blockers": [
    {
      "resource": "legacy-ingress",
      "reason": "Use networking.k8s.io/v1",
      "source": "fixtures/problematic/legacy.yaml"
    }
  ]
}
```

## Estrutura do `report.md`

O markdown gerado organiza a leitura em quatro blocos:

1. cabecalho com `target_version`
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

- falhar o job se `blockers` nao estiver vazio
- sinalizar aprovacao manual se `warnings` for maior que zero
- armazenar `report.json` como artefato de build
- publicar `report.md` no sumario do pipeline

## Limites do modelo atual

- o relatório ainda nao agrega findings por namespace ou aplicacao
- `target_version` ainda nao muda o catalogo de regras
- o formato markdown ainda nao inclui links, tabelas ou anotacoes de linha

## Leitura complementar

- [README.md](../README.md)
- [docs/architecture.md](architecture.md)
- [docs/roadmap.md](roadmap.md)
