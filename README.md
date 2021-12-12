# airflow-providers-siasg
Provider para Airflow que comunica com [SIASG](https://antigo.comprasgovernamentais.gov.br/index.php/comprasnet-siasg) e seus sistemas derivados

# Instalação

```shell
pip install airflow-providers-siasg
```

# Conteúdo

- Sub-provider para [DW-SIASG](https://dw.comprasnet.gov.br/dwcompras/servlet/mstrWeb)
    - Novo tipo de conexão "Conta do DW-SIASG"
    - Transfers de relatórios do DW-SIASG para arquivo e banco MongoDB

# Exemplos de uso

```python
task2 = DWSIASGRelatorioParaMongoOperator(
    task_id='task2',
    id_conexao='teste',
    id_relatorio='BFD128CD11EC5B5D670B0080EF6553F5',
    respostas_prompts=['160030', '160130'],
    timeout_segundos=120,
    id_conexao_mongo='teste_mongo',
    banco='teste_siasg',
    colecao='teste_siasg',
)
```

Para mais exemplos, consultar `airflow/providers/siasg/example_dags/dw.py`
