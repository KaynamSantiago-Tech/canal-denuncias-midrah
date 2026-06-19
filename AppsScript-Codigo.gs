/****************************************************************
 * Canal de Denúncias Midrah — Envio de e-mail via Gmail (Apps Script)
 *
 * Este script recebe os dados do formulário (do servidor no Render)
 * por HTTPS e envia o e-mail pelo Gmail da conta que publicar o script.
 *
 * COMO USAR:
 *  1. Acesse https://script.google.com  (logado em tecnologiamidrah@gmail.com)
 *  2. Novo projeto → apague o conteúdo e cole TODO este código.
 *  3. Implantar → Nova implantação → tipo "App da Web":
 *        - Executar como:  Eu (tecnologiamidrah@gmail.com)
 *        - Quem pode acessar:  Qualquer pessoa
 *     → Implantar → Autorizar acesso (permita o Gmail).
 *  4. Copie a URL do app da Web (termina em /exec) e envie para configurar.
 ****************************************************************/

var TOKEN = 'midrah-canal-2026';  // deve ser igual ao GAS_TOKEN do servidor

function doPost(e) {
  try {
    var p = JSON.parse(e.postData.contents);
    if (p.token !== TOKEN) {
      return _json({ result: 'forbidden' });
    }
    var options = {
      htmlBody: p.html,
      name: p.fromName || 'Canal de Denúncias Midrah'
    };
    if (p.logo_b64) {
      options.inlineImages = {
        logo: Utilities.newBlob(Utilities.base64Decode(p.logo_b64), 'image/png', 'logo.png')
      };
    }
    if (p.attachments && p.attachments.length) {
      options.attachments = p.attachments.map(function (a) {
        return Utilities.newBlob(
          Utilities.base64Decode(a.b64),
          a.mime || 'application/octet-stream',
          a.name
        );
      });
    }
    GmailApp.sendEmail(p.to, p.subject, p.text || '', options);
    return _json({ result: 'ok' });
  } catch (err) {
    return _json({ result: 'erro', detail: String(err) });
  }
}

function doGet(e) {
  return _json({ result: 'ok', service: 'Canal de Denuncias Midrah' });
}

function _json(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
