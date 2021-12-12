from typing import Any, List
import json

from airflow.models.baseoperator import BaseOperator
import humanize

from airflow.providers.siasg.dw.hooks.dw import DWSIASGHook


class DWSIASGRelatorioParaArquivoOperator(BaseOperator):
    '''Baixa um relatório do DW-SIASG para um arquivo local.

    :param id_conexao: id pra conexão do tipo "dw_siasg"
    :type id_conexao: str
    :param id_relatorio: id do relatório no DW-SIASG
    :type id_relatorio: str
    :param destino: caminho onde arquivo Excel será baixado. Pode ser um
    arquivo terminando em ".xlsx" ou um diretório terminando em "/"
    :type destino: str
    :param repostas_prompts: lista de respostas para prompts do relatório
    :type repostas_prompts: List[str]
    :param timeout_segundos: tempo máximo de espera em segundos
    :type timeout_segundos: int, opcional
    '''
    template_fields = ['id_relatorio', 'destino', 'respostas_prompts']

    id_conexao: str
    id_relatorio: str
    destino: str
    respostas_prompts: List[str]
    timeout_segundos: int

    def __init__(
        self,
        id_conexao: str,
        id_relatorio: str,
        destino: str,
        respostas_prompts: List[str] = None,
        timeout_segundos: int = 60,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.id_conexao = id_conexao
        self.id_relatorio = id_relatorio
        self.destino = destino
        self.respostas_prompts = respostas_prompts
        self.timeout_segundos = timeout_segundos

    def execute(self, context: Any) -> None:
        self.log.info(
            'Baixando relatório  "%s" para "%s" com respotas "%s"',
            self.id_relatorio, self.destino, self.respostas_prompts or ''
        )

        respostas_prompts = json.loads(self.respostas_prompts) \
            if isinstance(self.respostas_prompts, str) \
            else self.respostas_prompts

        with DWSIASGHook(self.id_conexao) as hook:
            local, tamanho = hook.baixa_para_excel(
                self.id_relatorio, self.destino, respostas_prompts,
                self.timeout_segundos
            )

        self.log.info('Download realizado com sucesso para "%s".', local)

        self.xcom_push(context, 'local', local)
        self.xcom_push(context, 'tamanho', tamanho)
        self.xcom_push(context, 'tamanho_texto', humanize.naturalsize(tamanho))
