# Projeto Bot Discord

Este é um bot Discord desenvolvido em Python para interagir com usuários, realizar buscas no YouTube e fornecer respostas usando uma inteligência artificial.

___
![B.O.BOT](/boticon.png)

## Requisitos

- Python 3.x
- Biblioteca discord.py
- Biblioteca requests
- Chave de API do YouTube
- Chave de API do OpenAI

## Instalação

1. Clone o repositório:

~~~
git clone https://github.com/seu-usuario/projeto-bot-discord.git
~~~

2. Instale as dependências:

~~~
pip install -r requirements.txt
~~~

3. Configure as chaves de API:

   - No arquivo `SECRET_KEY.py`, substitua `BOT_TOKEN` pela chave do bot Discord e `GPT_KEY` pela chave de API do OpenAI.

4. Execute o bot:

~~~
python bot.py
~~~


## Funcionalidades

- Comando `ping`: Retorna a resposta "Pong!" para verificar se o bot está online.
- Comando `youtube`: Realiza uma busca no YouTube e retorna os vídeos relacionados ao argumento fornecido.
- Comando `BOT`: Permite conversar com a IA usando a API do OpenAI.

## Contribuições

Contribuições são bem-vindas! Se você encontrar algum problema ou tiver alguma sugestão, sinta-se à vontade para abrir uma issue ou enviar um pull request.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
