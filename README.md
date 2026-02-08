# Projeto Bot Discord

Este é um bot Discord desenvolvido em Python para interagir com usuários, realizar buscas no YouTube e fornecer respostas usando uma inteligência artificial.

___
![B.O.BOT](/boticon.png)

## Requisitos

- Python 3.x
- Biblioteca discord.py
- Biblioteca requests
- LLM local (Ollama recomendado)

## Instalação

1. Clone o repositório:

~~~
git clone https://github.com/seu-usuario/projeto-bot-discord.git
~~~

2. Instale as dependências:

~~~
poetry install
~~~

3. Configure as chaves de API:

   - Crie um arquivo `.env` baseado em `.env.example` e preencha as variáveis:
     - `BOT_TOKEN`
     - `ID_CANAL`
     - `LLM_PROVIDER` (ollama|lmstudio|gpt4all)
     - `LLM_MODEL`
     - `LLM_TIMEOUT`

4. Execute o bot:

~~~
poetry run bobot
~~~

## Docker Compose

1. Crie o arquivo .env e configure as variáveis:

~~~
cp .env.example .env
~~~

2. Suba o bot com Docker Compose:

~~~
docker compose up --build -d
~~~

3. Verifique os logs:

~~~
docker compose logs -f
~~~

## Como usar

### Comandos com prefixo (!)

- `!comandos` — lista de comandos
- `!ola` — saudação
- `!versão` — versão do bot
- `!python` — documentação Python
- `!javascript` / `!js` — documentação JavaScript
- `!html` — documentação HTML
- `!css` — documentação CSS
- `!mongodb` / `!mongo` — documentação MongoDB
- `!csharp` / `!c#` — documentação C#
- `!c` — documentação C
- `!snippet <linguagem> [termo]` — snippets (30 seconds of code)
- `!pesquisa <consulta>` — busca no Google
- `!youtube <consulta>` — busca no YouTube
- `!calc <soma|sub|mult|div> <a> <b>` — calculadora
- `!run <linguagem> <código>` — executa código via Piston

### Comandos IA (prefixo !)

- `!pergunta <pergunta>` — pergunta técnica
- `!codigo <linguagem> <tema>` — exemplo de código
- `!debug <erro>` — diagnóstico de erro
- `!docs <tecnologia>` — documentação recomendada
- `!status` — status do LLM local

### LLM local (Ollama/LMS/GPT4All)

Defina no `.env`:

- `LLM_PROVIDER` (ollama | lmstudio | gpt4all)
- `LLM_MODEL`
- `LLM_TIMEOUT`
- `LLM_OLLAMA_URL`, `LLM_LMSTUDIO_URL`, `LLM_GPT4ALL_URL`
- `LLM_FALLBACKS` (opcional, lista separada por vírgula)

Exemplo:

```
LLM_PROVIDER=ollama
LLM_MODEL=deepseek-coder:6.7b
LLM_TIMEOUT=120
LLM_OLLAMA_URL=http://localhost:11434
```

## Estrutura do projeto

- Código principal: `src/bobot/`
- Scripts utilitários: `scripts/`
- Entrada do bot: `poetry run bobot` ou `python -m bobot`


## Funcionalidades

- Comandos de documentação e utilidades (Python, JS, HTML, CSS, MongoDB, C, C#)
- Snippets de referência
- Pesquisa no Google e YouTube
- Execução de código via Piston
- LLM local com Ollama/LMS/ GPT4All

## Roadmap (próximos passos)

- Sistema de perfis e modos (estudo/rápido)
- Histórico por canal
- Plugins
- /status
- /perfil

Arquitetura alvo:
- commands/
- services/
- adapters/
- ai/
- utils/
- storage/

## Contribuições

Contribuições são bem-vindas! Se você encontrar algum problema ou tiver alguma sugestão, sinta-se à vontade para abrir uma issue ou enviar um pull request.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
