# %% Definição de constantes

URL_BASE = 'https://dw.comprasnet.gov.br/dwcompras/servlet/mstrWeb'
SERVIDOR = '161.148.236.156'
PROJETO = 'SIASG+COMPRAS'


# %% Tentando realizar login na página do DW SIASG utilizando a biblioteca
# `requests`

import requests

login_params = {
    'Server': SERVIDOR,
    'Project': PROJETO,
    'Port': 0,
    'evt': '3067',
    'src': 'mstrWeb.3067',
    'group': 'export',
    'fastExport': 'true',
    'showOptionsPage': 'false',
    'reportID': '4D9286C311EC58F4AFF20080EF8593F3',
    'reportViewMode': '1',
    'uid': input('CPF: '),
    'pwd': input('Senha: ')
}
url = URL_BASE + '?' + '&'.join(
    f'{chave}={valor}' for chave, valor in login_params.items()
)

# %% Executa comando
response = requests.get(url, verify=False, allow_redirects=True)
