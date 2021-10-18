# ScriptMatricula
Script para fazer a matrícula na UFCG de forma automática.

## Instalação do Driver

**`Obs: Esse script utiliza o navegador Google Chrome`**

Para verificar sua versão do navegador, utilize o _site_ [WhatIsMyBrowser](https://www.whatismybrowser.com/detect/what-version-of-chrome-do-i-have);

Após descobrir sua versão, baixe no [site oficial](https://chromedriver.chromium.org/downloads) o _driver_ da **versão correspondente** e do **sistema operacional** que você utiliza. 

Com o _driver_ baixado no seu computador, será necessário adicioná-lo ao _path_ do seu computador.

### Linux
- Consultar os passos no _post_ a seguir: [Configurando o chromedriver no Ubuntu](https://medium.com/@marco.conviccao/configurando-o-chromedriver-no-ubuntu-7baaf2be7c68)

### Windows
1. Extraia o arquivo `.zip`.
2. Coloque dentro de uma pasta de sua preferência. 
   - Ex.: `Documentos > PastaDoDriver`
3. Copie a caminho dessa pasta.
   - Ex.: `C:\Users\seuNome\Documents\PastaDoDriver` 
4. Abra o menu iniciar ou pressione a tecla `Windows` e digite "Variáveis de ambiente" e selecione a opção do `Editar variáveis de ambiente do sistema`.
5. Na aba `Avançado` clique no botão `Variáveis de Ambiente...`.
6. Clique na variável `Path` e depois no botão `Editar...`.
7. Clique em `Novo` e cole o caminho do **passo 3**.
8. Prossiga clicando em `Ok` para ir fechando os menus abertos pelos passos anteriores. 

### Mac OS
- Adicionar o _driver_ em uma pasta de sua preferência e copiar o caminho dela para o código _python_ da _branch_ correspondente (ainda será criada).

## Execução

1. Edite o `dados.json` com sua informações correspondentes seguindo o padrão. 
   - Com cuidado para a última disciplina não ter uma vírgula no fim.
```json
[
  {
    "matricula": "111111111",
    "senha": "senha",
    "horarioDeAbertura": "06:00:00",
    "disciplinas": {
      "1111111 - 01": "Exemplo 01 com vírgula no final",
      "2222222 - 01": "Exemplo 02 com vírgula no final",
      "3333333 - 01": "Exemplo 03 SEM vírgula no final"
    }
  }
]
```

2. Execute o arquivo _python_ no terminal de sua preferência. 
   - Ou utilize o executável `.exe` (**Windows apenas**).
3. Seja feliz.

## Dependências

### Bibliotecas
- [Selenium](https://pypi.org/project/selenium/)
  - `pip install selenium`
- Json
- Time

### Ferramentas
- _[ChromeDriver](https://chromedriver.chromium.org/downloads)_
