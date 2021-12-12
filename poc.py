# %% Definição de constantes

URL_BASE = 'https://dw.comprasnet.gov.br/dwcompras/servlet/mstrWeb'
SERVIDOR = '161.148.236.156'
PROJETO = 'SIASG+COMPRAS'


# %% Tentando realizar login na página do DW SIASG utilizando a biblioteca
# `requests`
from selenium import webdriver

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
print(url)

# %% Executa comando
from webdriver_manager.firefox import GeckoDriverManager


profile = webdriver.FirefoxProfile()
profile.set_preference('browser.download.folderList', 2)
profile.set_preference('browser.download.manager.showWhenStarting', False)
profile.set_preference('browser.download.dir', '/home/carlos/Downloads2')
profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=UTF-8')

options = webdriver.FirefoxOptions()
options.headless = True

driver = webdriver.Firefox(
    firefox_profile=profile,
    options=options,
    executable_path=GeckoDriverManager().install()
)

driver.get(url)

input()

driver.close()
