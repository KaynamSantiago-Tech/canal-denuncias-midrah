# Publicar o Canal de Denúncias na internet (Render)

O código já está num repositório **privado** no GitHub e pronto para o Render.
Siga os passos abaixo (≈5 minutos) para gerar o **link público**.

## 1. Criar conta no Render
1. Acesse **https://render.com** → **Get Started** → **Sign in with GitHub**
   (use a conta GitHub `KaynamSantiago-Tech`, onde está o repositório).
2. Autorize o Render a acessar seus repositórios.

## 2. Criar o serviço a partir do Blueprint
1. No painel do Render: **New +** → **Blueprint**.
2. Selecione o repositório **canal-denuncias-midrah**.
3. O Render lê o arquivo `render.yaml` e já preenche tudo. Clique em **Apply**.
4. Ele vai pedir o valor do segredo **SMTP_PASS** → cole a **Senha de App** do
   Gmail (as 16 letras, sem espaços). É a mesma que está no `iniciar-servidor.bat`
   desta pasta (linha `set SMTP_PASS=...`).
5. Confirme. O deploy começa sozinho.

> Se preferir sem Blueprint: **New + → Web Service** → escolha o repo →
> Runtime **Python**, Build `pip install -r requirements.txt`, Start
> `python servidor.py`, e adicione as variáveis de ambiente manualmente
> (veja a lista no `render.yaml`), incluindo `SMTP_PASS`.

## 3. Pegar o link
Ao terminar, o Render mostra a URL pública, algo como:
**https://canal-denuncias-midrah.onrender.com**

Esse é o link para compartilhar com os executivos/colaboradores.

## Observações importantes
- **Plano gratuito:** o serviço “hiberna” após ~15 min sem uso; o primeiro acesso
  depois disso leva ~30–50s para “acordar”. Os acessos seguintes são instantâneos.
  Para evitar isso, dá para subir ao plano pago mais simples depois.
- **Segurança:** a senha de app fica só no Render (variável de ambiente), nunca no
  código. Se precisar trocar: gere outra em myaccount.google.com/apppasswords e
  atualize a variável `SMTP_PASS` no painel do Render.
- **Domínio próprio (opcional):** dá para apontar `denuncias.midrah.com.br` para
  esse serviço em Settings → Custom Domains (precisa de um registro DNS).
- **Atualizações:** qualquer mudança que eu enviar ao GitHub é publicada
  automaticamente pelo Render (deploy contínuo).
