from typing import Dict

from airflow.hooks.base import BaseHook


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
