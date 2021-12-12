from datetime import datetime
from time import sleep
from typing import Dict, Tuple
import os
import re
import shutil
import tempfile

from airflow.hooks.base import BaseHook
from airflow.exceptions import AirflowException
from seleniumwire import webdriver
from selenium.common.exceptions import TimeoutException
from webdriver_manager.firefox import GeckoDriverManager


class DWSIASGHook(BaseHook):
    '''Hook para interação com o DW SIASG.

    :param id_conexao: id pra conexão do tipo "dw_siasg"

    Uso
    ---
    O hook pode ser instanciado de duas formas:

    1. Para simples consulta de parâmetros:

    .. code-block:: python
        :linenos:

        hook = DWSIASGHook('id_conexao')

    2. Para operações:

    .. code-block:: python
        :linenos:

        with DWSIASGHook('id_conexao') as hook:
            # Performar operações
    '''
    conn_name_attr = 'dw_siasg'
    default_conn_name = 'dw_siasg_default'
    conn_type = 'dw_siasg'
    hook_name = 'Conta do DW-SIASG'

    URL = 'https://dw.comprasnet.gov.br/dwcompras/servlet/mstrWeb'
    PAYLOAD = {
        'Server': '161.148.236.156',
        'Project': 'SIASG+COMPRAS',
        'Port': 0,
        'evt': '3067',
        'src': 'mstrWeb.3067',
        'group': 'export',
        'fastExport': 'true',
        'showOptionsPage': 'false',
        'reportID': None,
        'reportViewMode': '1',
        'uid': None,
        'pwd': None,
    }

    id_conexao: str
    _diretorio_download: str
    _navegador: webdriver.Firefox

    def __init__(self, id_conexao: str) -> None:
        super().__init__()
        self.id_conexao = id_conexao

    @property
    def cpf(self) -> str:
        '''Retorna o CPF sempre atualizado.'''
        connection = self.get_connection(self.id_conexao)
        return connection.login

    @property
    def senha(self) -> str:
        '''Retorna a senha sempre atualizada.'''
        connection = self.get_connection(self.id_conexao)
        return connection.password

    def __enter__(self) -> 'DWSIASGHook':
        '''Inicia navegador.'''
        self._diretorio_download = os.path.join(
            tempfile.gettempdir(), next(tempfile._get_candidate_names())
        )
        os.makedirs(self._diretorio_download, exist_ok=True)

        self.log.info(
            'Instanciando navegador do Firefox com diretório de downloads em '
            '%s', self._diretorio_download
        )

        opcoes = webdriver.FirefoxOptions()
        opcoes.set_preference('browser.download.folderList', 2)
        opcoes.set_preference(
            'browser.download.manager.showWhenStarting', False
        )
        opcoes.set_preference('browser.download.dir', self._diretorio_download)
        opcoes.set_preference(
            'browser.helperApps.neverAsk.saveToDisk',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            ';charset=UTF-8'
        )
        opcoes.headless = True

        self._navegador = webdriver.Firefox(
            options=opcoes,
            executable_path=GeckoDriverManager().install()
        )

        return self

    def __exit__(self, *args, **kwargs) -> None:
        '''Encerra navegador e exclui recursos.'''
        self.log.info(
            'Encerrando navegador e limpando recursos em "%s"',
            self._diretorio_download
        )

        self._navegador.close()
        shutil.rmtree(self._diretorio_download, ignore_errors=True)

    def baixa_para_excel(
        self,
        id_relatorio: str,
        destino: str,
        timeout_segundos: int = 60
    ) -> Tuple[str, int]:
        '''Baixa o relatório para um arquivo local dentro de um timeout.

        :param id_relatorio: id do relatório no DW-SIASG
        :type id_relatorio: str
        :param destino: caminho onde arquivo Excel será baixado. Pode ser um
        arquivo terminando em ".xlsx" ou um diretório terminando em "/"
        :type id_relatorio: str
        :param timeout_segundos: tempo máximo de espera em segundos
        :type timeout_segundos: int, opcional
        :return: caminho absoluto e tamanho em bytes do arquivo
        :rtype: Tuple[str, int]
        '''
        self.log.info(
            'Baixando relatório com ID "%s" para "%s"',
            id_relatorio, destino
        )

        payload = self.PAYLOAD.copy()
        payload.update({
            'reportID': id_relatorio,
            'uid': self.cpf,
            'pwd': self.senha
        })
        url = self.URL + '?' + '&'.join(
            f'{chave}={valor}' for chave, valor in payload.items()
        )

        self._navegador.get(url)

        inicio = datetime.now()

        try:
            requisicao = self._navegador.wait_for_request(
                'https://dw.comprasnet.gov.br/dwcompras/export/',
                timeout=timeout_segundos
            )
        except TimeoutException:
            raise AirflowException(
                f'Não foi possível gerar o relatório "{id_relatorio}" em até '
                f'{timeout_segundos} segundos'
            )

        nome = re.findall(
            r'attachment;filename\*=([^;]*);',
            requisicao.response.headers.get('Content-Disposition', '')
        )[0]
        local = os.path.join(self._diretorio_download, nome)
        tamanho = requisicao.response.headers['total-length']

        # Esperar download do arquivo finalizar
        while not os.path.getsize(local) != tamanho:
            if (datetime.now() - inicio).seconds > timeout_segundos:
                raise AirflowException(
                    'Não foi possível realizar o download do relatorio '
                    f'"{id_relatorio}" dentro de {timeout_segundos} segundos'
                )

            sleep(1)

        os.makedirs(os.path.dirname(destino), exist_ok=True)
        caminho_final = shutil.copy(local, destino)

        self.log.info(
            'Relatório "%s" baixado para "%s" com sucesso',
            id_relatorio, caminho_final
        )

        return str(caminho_final), tamanho

    @staticmethod
    def get_ui_field_behaviour() -> Dict[str, str]:
        '''Customiza comportamento dos formulários.'''

        return {
            'hidden_fields': [
                'host', 'port', 'schema', 'extra', 'description'
            ],
            'relabeling': {
                'conn_id': 'ID da conexão',
                'conn_type': 'Tipo de conexão',
                'login': 'CPF',
                'password': 'Senha'
            }
        }


if __name__ == '__main__':
    with DWSIASGHook('teste') as hook:
        hook.baixa_para_excel(
            '4D9286C311EC58F4AFF20080EF8593F3', '/home/carlos/Download3/', 6
        )