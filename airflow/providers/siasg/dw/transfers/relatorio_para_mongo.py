from datetime import datetime
from typing import Any, List
import json
import tempfile

from airflow.models.baseoperator import BaseOperator
from airflow.providers.mongo.hooks.mongo import MongoHook
import pandas

from airflow.providers.siasg.dw.hooks.dw import DWSIASGHook


class DWSIASGRelatorioParaMongoOperator(BaseOperator):
    '''Baixa um relatório do DW-SIASG para um banco Mongo

    :param id_conexao: id pra conexão do tipo "dw_siasg"
    :type id_conexao: str
    :param id_relatorio: id do relatório no DW-SIASG
    :type id_relatorio: str
    :param id_conexao_mongo: id para conexão do tipo "mongo"
    :type id_conexao_mongo
    :param banco: Nome do banco
    :type banco: str
    :param colecao: Nome da coleção
    :type colecao: str
    :param repostas_prompts: lista de respostas para prompts do relatório
    :type repostas_prompts: List[str]
    :param timeout_segundos_segundos: tempo máximo de espera em segundos
    :type timeout_segundos_segundos: int, opcional
    :param truncar_colecao: `True` se coleção deve ser truncada antes da
    inserção e `False` caso contrário
    :type truncar_colecao: bool
    '''
    template_fields = [
        'id_relatorio', 'respostas_prompts', 'banco', 'colecao'
    ]

    id_conexao: str
    id_relatorio: str
    respostas_prompts: List[str]
    timeout_segundos: int

    id_conexao_mongo: str
    banco: str
    colecao: str
    truncar_colecao: bool

    def __init__(
        self,
        id_conexao: str,
        id_relatorio: str,
        id_conexao_mongo: str,
        banco: str = None,
        colecao: str = 'test',
        respostas_prompts: List[str] = None,
        timeout_segundos: int = 60,
        truncar_colecao: bool = False,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)

        self.id_conexao = id_conexao
        self.id_relatorio = id_relatorio
        self.respostas_prompts = respostas_prompts
        self.timeout_segundos = timeout_segundos

        self.id_conexao_mongo = id_conexao_mongo
        self.banco = banco
        self.colecao = colecao
        self.truncar_colecao = truncar_colecao

    def execute(self, context: Any) -> None:
        self.log.info(
            'Baixando relatório "%s" para coleção do mongo "%s" com as '
            'seguintes respostas para prompts: "%s"%s',
            self.id_relatorio, self.colecao, self.respostas_prompts,
            '. Truncando coleção' if self.truncar_colecao else ''
        )

        respostas_prompts = json.loads(self.respostas_prompts) \
            if isinstance(self.respostas_prompts, str) \
            else self.respostas_prompts

        with tempfile.NamedTemporaryFile(mode='wb') as arquivo:
            instante = datetime.now()

            with DWSIASGHook(self.id_conexao) as hook:
                local, _ = hook.baixa_para_excel(
                    self.id_relatorio, arquivo.name, respostas_prompts,
                    self.timeout_segundos
                )

            df = pandas.read_excel(local)

        df.columns = df.columns.str.replace('.', '', regex=False)
        df['Timestamp'] = instante

        with MongoHook(self.id_conexao_mongo) as hook:
            if self.truncar_colecao:
                hook.delete_many(self.colecao, {}, self.banco)

            inseridos = hook.insert_many(
                self.colecao, df.to_dict('records'), self.banco
            ).inserted_ids

        self.log.info(
            'Relatório transferido com sucesso, tendo produzido %s registros',
            len(inseridos)
        )

        self.xcom_push(context, 'registros_inseridos', len(inseridos))
