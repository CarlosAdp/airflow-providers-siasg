from typing import Dict
import os
import shutil
import tempfile

from airflow.hooks.base import BaseHook
from selenium import webdriver
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

        perfil = webdriver.FirefoxProfile()
        perfil.set_preference('browser.download.folderList', 2)
        perfil.set_preference(
            'browser.download.manager.showWhenStarting', False
        )
        perfil.set_preference('browser.download.dir', self._diretorio_download)
        perfil.set_preference(
            'browser.helperApps.neverAsk.saveToDisk',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            ';charset=UTF-8'
        )

        opcoes = webdriver.FirefoxOptions()
        opcoes.headless = True

        self._navegador = webdriver.Firefox(
            firefox_profile=perfil,
            options=opcoes,
            executable_path=GeckoDriverManager().install()
        )

        return self

    def __exit__(self, *args, **kwargs) -> None:
        '''Encerra navegador e exclui recursos.'''
        self._navegador.close()
        shutil.rmtree(self._diretorio_download, ignore_errors=True)

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
