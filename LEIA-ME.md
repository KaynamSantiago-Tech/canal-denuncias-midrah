# Canal de Denúncias Corporativo — Midrah Investimentos

Solução de canal de denúncias em conformidade com a **Lei nº 14.457/2022**
(Programa Emprega + Mulheres) e a **LGPD (Lei nº 13.709/2018)**.

**Como funciona:** o colaborador acessa um formulário (anônimo ou identificado),
preenche e envia. A cada envio, o sistema **monta um e-mail que replica o mesmo
formato do formulário** (mesmo cabeçalho, logo e campos) e envia, com os anexos,
para **denuncias.midrah@midrah.com.br**. Um número de **protocolo** é gerado e
mostrado ao denunciante. **Não há planilha** — tudo vai no corpo do e-mail.

---

## 📁 Arquivos desta pasta

**Tudo é feito em Python.** O formulário (HTML) e a logo ficam embutidos dentro
do `servidor.py` — não há arquivos `.html` ou `.png` soltos.

| Arquivo | Para que serve |
|---|---|
| **servidor.py** | **Aplicação completa**: serve o formulário (logo embutida), gera protocolo e envia o e-mail. |
| **iniciar-servidor.bat** | Atalho para ligar o sistema (duplo clique). |
| **emails_pendentes/** | (criada automaticamente) e-mails salvos quando o SMTP ainda não envia. |
| **Schema-SQL-Server.sql** | *Opcional/futuro* — estrutura caso um dia queira também armazenar em banco. Não é necessário para o fluxo por e-mail. |

---

## ▶️ Como colocar no ar

1. Dê **duplo clique em `iniciar-servidor.bat`** (ou rode `python servidor.py`).
2. Abra no navegador: **http://localhost:8000**
3. Preencha e envie. O e-mail formatado vai para `denuncias.midrah@midrah.com.br`.

---

## ✉️ Envio de e-mail (SMTP) — Gmail · ✅ CONFIGURADO E FUNCIONANDO

O `servidor.py` está configurado e o envio foi **testado com sucesso**:

```
SMTP_HOST = smtp.gmail.com   (porta 587)
SMTP_USER = tecnologiamidrah@gmail.com
SMTP_PASS = (Senha de App de 16 letras já configurada)
Remetente = Canal de Denúncias Midrah <tecnologiamidrah@gmail.com>
Destino   = denuncias.midrah@midrah.com.br
```

A senha usada é uma **Senha de App** do Google (não é a senha de login da conta).
Se um dia precisar trocá-la: ative a Verificação em duas etapas na conta e gere
uma nova em **myaccount.google.com/apppasswords**, depois cole no campo `SMTP_PASS`.

> 🔐 **Segurança:** o `servidor.py` contém a Senha de App. Mantenha esta pasta com
> acesso restrito (NTFS) e não a compartilhe. Se a senha vazar, revogue-a na conta
> Google e gere outra — a senha de login do Gmail continua independente.

---

## 🌐 Disponibilizar o link para os colaboradores

- **Rede interna:** rode o `servidor.py` numa máquina sempre ligada e divulgue
  `http://<ip-do-servidor>:8000`.
- **Produção (recomendado):** publique atrás de **HTTPS** com um link amigável,
  ex.: `https://denuncias.midrah.com.br`.
- O formulário já vem com `noindex` (não aparece em buscadores).

---

## 🔒 Conformidade

- **Anônima ou identificada** — o nome é sempre **opcional**; em modo anônimo o
  sistema **não registra IP** nem identifica o denunciante.
- **Sigilo** — destino exclusivo `denuncias.midrah@midrah.com.br` (acesso restrito
  a RH e Diretoria). O e-mail traz aviso de confidencialidade.
- **Protocolo + data/hora** gerados automaticamente a cada denúncia.
- Campos do formulário: tipo, descrição, data, pessoas envolvidas, local, anexos
  de evidências e identificação opcional.
