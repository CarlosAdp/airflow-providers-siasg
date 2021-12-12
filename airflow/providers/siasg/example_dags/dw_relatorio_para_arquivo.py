from datetime import datetime
import os

from airflow.decorators import dag

from airflow.providers.siasg.dw.transfers.relatorio_para_arquivo \
    import DWSIASGRelatorioParaArquivoOperator


@dag(schedule_interval=None, start_date=datetime(2021, 12, 10))
def teste_siasg():
    task1 = DWSIASGRelatorioParaArquivoOperator(
        task_id='task1',
        id_conexao='teste',
        id_relatorio='BFD128CD11EC5B5D670B0080EF6553F4',
        destino=os.path.expanduser('~/Downloads'),
        respostas_prompts=['160030', '160130']
    )

    task1


dag = teste_siasg()
