from datetime import datetime
import os

from airflow.decorators import dag

from airflow.providers.siasg.dw.transfers.relatorio_para_arquivo \
    import DWSIASGRelatorioParaArquivoOperator
from airflow.providers.siasg.dw.transfers.relatorio_para_mongo \
    import DWSIASGRelatorioParaMongoOperator


@dag(schedule_interval=None, start_date=datetime(2021, 12, 10))
def teste_siasg():
    task1 = DWSIASGRelatorioParaArquivoOperator(
        task_id='task1',
        id_conexao='teste',
        id_relatorio='BFD128CD11EC5B5D670B0080EF6553F4',
        destino=os.path.expanduser('~/Downloads'),
        respostas_prompts=['160030', '160130']
    )

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

    task1
    task2


dag = teste_siasg()
