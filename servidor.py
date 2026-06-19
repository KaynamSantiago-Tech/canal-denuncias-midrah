# -*- coding: utf-8 -*-
"""
Canal de Denúncias Corporativo — Midrah Investimentos
================================================================
APLICAÇÃO ÚNICA EM PYTHON (sem arquivos .html/.png separados).
Este único arquivo:
  • serve o FORMULÁRIO (HTML embutido abaixo, com a logo embutida);
  • gera um número de PROTOCOLO e registra data/hora;
  • monta um e-mail que REPLICA O MESMO FORMATO DO FORMULÁRIO no corpo
    (mesmo cabeçalho, logo e campos), com os anexos;
  • envia para  denuncias.midrah@midrah.com.br

Usa apenas a biblioteca padrão do Python — nada para instalar.

Como rodar (Windows):  duplo clique em  iniciar-servidor.bat
                        ou no terminal:  python servidor.py
Depois abra no navegador:  http://localhost:8000
================================================================
"""

import os, json, ssl, smtplib, base64, threading, mimetypes, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from email.message import EmailMessage
from email.utils import make_msgid

# ===================== CONFIGURAÇÃO =====================
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8000"))   # a nuvem (Render) injeta a porta via env

EMAIL_DESTINO = os.environ.get("EMAIL_DESTINO", "denuncias.midrah@midrah.com.br")

# --- Envio de e-mail via Gmail (SMTP) ---
# IMPORTANTE: o Gmail NÃO aceita a senha normal da conta. Use uma SENHA DE APP
# (16 letras) gerada em https://myaccount.google.com/apppasswords
# A SENHA NÃO FICA NO CÓDIGO: ela vem da variável de ambiente SMTP_PASS
#   • Local: definida no iniciar-servidor.bat
#   • Render (nuvem): definida em Environment > Environment Variables
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "tecnologiamidrah@gmail.com")
SMTP_PASS = os.environ.get("SMTP_PASS", "")   # <-- definida por variável de ambiente (não no código)
EMAIL_REMETENTE = os.environ.get("EMAIL_REMETENTE",
                                 "Canal de Denúncias Midrah <tecnologiamidrah@gmail.com>")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PEND_DIR = os.path.join(BASE_DIR, "emails_pendentes")

# Logo da Midrah embutida (base64 PNG) — injetada automaticamente.
LOGO_B64 = "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"
LOGO_DATA_URI = "data:image/png;base64," + LOGO_B64
# =======================================================

_lock = threading.Lock()


# ===================== PÁGINA DO FORMULÁRIO (HTML embutido) =====================
HTML_PAGE = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="robots" content="noindex, nofollow" />
<title>Canal de Denúncias · Midrah Investimentos</title>
<link rel="icon" href="midrah-logo.png" />
<style>
  :root{
    --navy:#14233D; --navy2:#0E1B30; --azure:#2090D0; --azure-dark:#1577B0;
    --azure-soft:#E8F2FB; --bg:#EEF3F8; --card:#FFFFFF; --line:#E2E8F0;
    --text:#1F2A37; --muted:#64748B; --danger:#B00020; --ok:#1E8E5A;
    --radius:14px; --shadow:0 10px 30px rgba(20,35,61,.08);
  }
  *{box-sizing:border-box}
  html,body{margin:0;padding:0}
  body{
    font-family:"Segoe UI",system-ui,-apple-system,Roboto,Arial,sans-serif;
    background:var(--bg); color:var(--text); line-height:1.55;
    -webkit-font-smoothing:antialiased;
  }
  .wrap{max-width:820px;margin:0 auto;padding:24px 18px 60px}
  .header{
    background:linear-gradient(135deg,var(--navy) 0%,var(--navy2) 45%,var(--azure-dark) 130%);
    border-radius:var(--radius); color:#fff; padding:30px 32px;
    box-shadow:var(--shadow); position:relative; overflow:hidden;
  }
  .header::after{content:"";position:absolute;right:-60px;top:-60px;width:220px;height:220px;
    background:radial-gradient(circle,rgba(32,144,208,.45),transparent 70%);border-radius:50%}
  .brandbar{display:flex;align-items:center;gap:14px;margin-bottom:18px}
  .brandbar img{height:30px;filter:brightness(0) invert(1);opacity:.96}
  .brandbar .div{width:1px;height:26px;background:rgba(255,255,255,.28)}
  .brandbar span{font-size:13px;letter-spacing:.5px;color:#cfe0f0}
  .header h1{margin:0;font-size:26px;font-weight:700;letter-spacing:.2px}
  .header p.sub{margin:8px 0 0;font-size:14.5px;color:#d6e4f2;max-width:600px}
  .card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
    box-shadow:var(--shadow);padding:26px 28px;margin-top:18px}
  .notice{background:var(--azure-soft);border:1px solid #cfe5f6;border-radius:12px;
    padding:16px 18px;font-size:14px;color:#234}
  .notice strong{color:var(--navy)}
  .notice .lock{display:inline-flex;align-items:center;gap:8px;font-weight:600;color:var(--azure-dark);margin-bottom:6px}
  h2.section{font-size:16px;color:var(--navy);margin:0 0 4px;font-weight:700}
  .section-desc{font-size:13px;color:var(--muted);margin:0 0 18px}
  label{display:block;font-size:13.5px;font-weight:600;color:#33404f;margin:0 0 6px}
  .req{color:var(--danger);font-weight:700}
  .opt{color:var(--muted);font-weight:500;font-size:12px}
  .field{margin-bottom:18px}
  input[type=text],input[type=email],input[type=tel],input[type=date],select,textarea{
    width:100%;padding:11px 13px;font-size:14.5px;font-family:inherit;color:var(--text);
    background:#fff;border:1px solid #cdd6e2;border-radius:10px;transition:.15s;
  }
  textarea{min-height:130px;resize:vertical}
  input:focus,select:focus,textarea:focus{outline:none;border-color:var(--azure);
    box-shadow:0 0 0 3px rgba(32,144,208,.15)}
  .hint{font-size:12px;color:var(--muted);margin-top:5px}
  .modes{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:6px}
  .mode{border:1.5px solid #cdd6e2;border-radius:12px;padding:14px 16px;cursor:pointer;
    display:flex;gap:12px;align-items:flex-start;transition:.15s;background:#fff}
  .mode:hover{border-color:var(--azure)}
  .mode input{margin-top:3px;accent-color:var(--azure)}
  .mode.active{border-color:var(--azure);background:var(--azure-soft);box-shadow:0 0 0 3px rgba(32,144,208,.12)}
  .mode .t{font-weight:700;font-size:14px;color:var(--navy)}
  .mode .d{font-size:12.5px;color:var(--muted);margin-top:2px}
  @media(max-width:560px){.modes{grid-template-columns:1fr}}
  #idfields{display:none;border-left:3px solid var(--azure);padding-left:18px;margin-top:6px}
  #idfields.show{display:block;animation:fade .2s ease}
  @keyframes fade{from{opacity:0;transform:translateY(-4px)}to{opacity:1}}
  .filebox{border:1.5px dashed #b9c6d6;border-radius:12px;padding:18px;text-align:center;background:#fafcfe;cursor:pointer;transition:.15s}
  .filebox:hover{border-color:var(--azure);background:var(--azure-soft)}
  .filebox .ic{font-size:26px}
  .filebox small{color:var(--muted)}
  #filelist{margin-top:10px;font-size:13px}
  #filelist .f{display:flex;justify-content:space-between;align-items:center;background:#f1f5fa;border:1px solid var(--line);border-radius:8px;padding:7px 11px;margin-top:6px}
  #filelist .f button{border:none;background:none;color:var(--danger);cursor:pointer;font-size:16px;line-height:1}
  .consent{display:flex;gap:11px;align-items:flex-start;background:#fbfcfe;border:1px solid var(--line);border-radius:12px;padding:14px 16px}
  .consent input{margin-top:3px;width:18px;height:18px;accent-color:var(--azure);flex:none}
  .consent label{font-weight:500;font-size:13px;color:#3a4756;margin:0}
  .submit{width:100%;margin-top:8px;padding:15px;font-size:16px;font-weight:700;color:#fff;
    background:linear-gradient(135deg,var(--azure) 0%,var(--azure-dark) 100%);
    border:none;border-radius:12px;cursor:pointer;transition:.15s;letter-spacing:.3px}
  .submit:hover{filter:brightness(1.05)}
  .submit:disabled{opacity:.6;cursor:not-allowed}
  .err-msg{color:var(--danger);font-size:12.5px;margin-top:5px;display:none}
  .field.invalid input,.field.invalid select,.field.invalid textarea{border-color:var(--danger)}
  .field.invalid .err-msg{display:block}
  .formfoot{font-size:12px;color:var(--muted);text-align:center;margin-top:18px;line-height:1.6}
  #success{display:none}
  .succ-ic{width:64px;height:64px;border-radius:50%;background:#e7f6ee;color:var(--ok);
    display:flex;align-items:center;justify-content:center;font-size:34px;margin:0 auto 14px}
  .proto{font-size:13px;color:var(--muted);text-align:center;margin-top:18px}
  .proto .code{display:block;font-size:24px;font-weight:800;letter-spacing:1px;color:var(--navy);margin-top:6px;font-family:"Consolas",monospace}
  .btn-sec{display:inline-block;margin-top:18px;padding:11px 20px;border:1.5px solid var(--azure);
    color:var(--azure-dark);background:#fff;border-radius:10px;font-weight:600;cursor:pointer;font-size:14px}
  .pagefoot{text-align:center;color:var(--muted);font-size:12px;margin-top:26px;line-height:1.7}
  .pagefoot img{height:18px;vertical-align:middle;opacity:.55;margin-right:6px}
</style>
</head>
<body>
<div class="wrap">
  <header class="header">
    <div class="brandbar">
      <img src="midrah-logo.png" alt="Midrah" />
      <div class="div"></div>
      <span>Investimentos</span>
    </div>
    <h1>Canal de Denúncias</h1>
    <p class="sub">Um espaço seguro, confidencial e acessível para o registro de situações
    incompatíveis com nossos valores. Em conformidade com a Lei nº 14.457/2022.</p>
  </header>

  <div class="card">
    <div class="notice">
      <div class="lock">🔒 Sua segurança e o seu sigilo são prioridade</div>
      Este canal recebe denúncias sobre <strong>assédio sexual, assédio moral, discriminação,
      violação do Código de Conduta</strong> e outras situações incompatíveis com os valores da empresa.
      As informações são tratadas com total confidencialidade e o acesso é <strong>exclusivo do RH e da Diretoria</strong>.
      Você pode denunciar de forma <strong>anônima</strong> ou identificada — a identificação é sempre opcional.
    </div>
  </div>

  <form id="form" class="card" novalidate>
    <div class="field">
      <h2 class="section">Como você deseja registrar a denúncia?</h2>
      <p class="section-desc">Escolha uma das opções. Em ambos os casos, todas as informações são sigilosas.</p>
      <div class="modes">
        <label class="mode active" id="m-anon">
          <input type="radio" name="modo" value="Anônima" checked />
          <div><div class="t">Anônima</div><div class="d">Não informo meus dados pessoais</div></div>
        </label>
        <label class="mode" id="m-id">
          <input type="radio" name="modo" value="Identificada" />
          <div><div class="t">Identificada</div><div class="d">Desejo me identificar (opcional)</div></div>
        </label>
      </div>
      <div id="idfields">
        <div class="field">
          <label>Nome <span class="opt">(opcional — só preencha se quiser)</span></label>
          <input type="text" name="nome" autocomplete="off" />
        </div>
        <div class="field">
          <label>E-mail para contato <span class="opt">(opcional)</span></label>
          <input type="email" name="email" autocomplete="off" placeholder="seunome@exemplo.com" />
        </div>
        <div class="field">
          <label>Telefone <span class="opt">(opcional)</span></label>
          <input type="tel" name="telefone" autocomplete="off" />
        </div>
        <div class="field">
          <label>Cargo / Setor <span class="opt">(opcional)</span></label>
          <input type="text" name="cargo" autocomplete="off" />
        </div>
      </div>
    </div>

    <hr style="border:none;border-top:1px solid var(--line);margin:8px 0 22px" />

    <h2 class="section">Sobre a ocorrência</h2>
    <p class="section-desc">Os campos marcados com <span class="req">*</span> são obrigatórios.</p>

    <div class="field" id="f-tipo">
      <label>Tipo da ocorrência <span class="req">*</span></label>
      <select name="tipo" required>
        <option value="" disabled selected>Selecione...</option>
        <option>Assédio sexual</option>
        <option>Assédio moral</option>
        <option>Discriminação</option>
        <option>Violação do Código de Conduta</option>
        <option>Outras situações incompatíveis com os valores da empresa</option>
      </select>
      <div class="err-msg">Selecione o tipo da ocorrência.</div>
    </div>

    <div class="field" id="f-data">
      <label>Data da ocorrência <span class="req">*</span></label>
      <input type="date" name="data_ocorrencia" required />
      <div class="hint">Se não souber a data exata, informe uma data aproximada.</div>
      <div class="err-msg">Informe a data da ocorrência.</div>
    </div>

    <div class="field">
      <label>Local / Setor onde ocorreu <span class="opt">(opcional)</span></label>
      <input type="text" name="local" placeholder="Ex.: escritório, setor comercial, evento externo..." />
    </div>

    <div class="field" id="f-pessoas">
      <label>Pessoas envolvidas <span class="req">*</span></label>
      <textarea name="pessoas" required placeholder="Quem esteve envolvido (denunciados, testemunhas...). Se preferir não nomear, descreva cargos/funções."></textarea>
      <div class="err-msg">Descreva as pessoas envolvidas.</div>
    </div>

    <div class="field" id="f-desc">
      <label>Descrição dos fatos <span class="req">*</span></label>
      <textarea name="descricao" required placeholder="Descreva o que aconteceu com o máximo de detalhes possível: o que, como, quando, onde e com que frequência."></textarea>
      <div class="err-msg">Descreva os fatos ocorridos.</div>
    </div>

    <div class="field">
      <label>Evidências / Anexos <span class="opt">(opcional)</span></label>
      <div class="filebox" id="filebox">
        <div class="ic">📎</div>
        <div>Clique para anexar arquivos</div>
        <small>Imagens, PDF, documentos, áudios · até 10 MB no total</small>
      </div>
      <input type="file" id="fileinput" multiple style="display:none" />
      <div id="filelist"></div>
    </div>

    <div class="field consent" id="f-consent">
      <input type="checkbox" id="consent" required />
      <label for="consent">Declaro que as informações prestadas são verdadeiras e estou ciente de que este
      canal é sigiloso e de acesso restrito ao RH e à Diretoria da Midrah Investimentos, conforme a
      Lei nº 14.457/2022 e a LGPD (Lei nº 13.709/2018). <span class="req">*</span></label>
    </div>
    <div class="err-msg" id="consent-err" style="margin:-8px 0 14px">É necessário confirmar a ciência acima.</div>

    <button type="submit" class="submit" id="btn">Enviar denúncia com segurança</button>
    <div class="formfoot">
      🔐 Conexão tratada de forma confidencial · Um número de protocolo será gerado ao final.
    </div>
  </form>

  <div class="card" id="success">
    <div class="succ-ic">✓</div>
    <h2 class="section" style="text-align:center;font-size:20px">Denúncia registrada com sucesso</h2>
    <p class="section-desc" style="text-align:center">
      Sua denúncia foi recebida e encaminhada com segurança ao RH e à Diretoria.
      Ela será apurada com sigilo e tratamento adequado.
    </p>
    <div class="proto">
      Guarde o seu número de protocolo:
      <span class="code" id="proto-code">—</span>
    </div>
    <div style="text-align:center">
      <button class="btn-sec" onclick="window.print()">🖨️ Salvar / imprimir comprovante</button>
    </div>
  </div>

  <div class="pagefoot">
    <img src="midrah-logo.png" alt="Midrah" />
    Midrah Investimentos · Canal de Denúncias Corporativo<br/>
    Compromisso com a ética, a integridade e um ambiente de trabalho seguro e livre de assédio e discriminação.
  </div>
</div>

<script>
const ENDPOINT = "/enviar";
const MAX_TOTAL_BYTES = 10 * 1024 * 1024;
const form = document.getElementById('form');
const mAnon = document.getElementById('m-anon');
const mId = document.getElementById('m-id');
const idfields = document.getElementById('idfields');
function syncMode(){
  const id = mId.querySelector('input').checked;
  idfields.classList.toggle('show', id);
  mId.classList.toggle('active', id);
  mAnon.classList.toggle('active', !id);
}
mAnon.querySelector('input').addEventListener('change', syncMode);
mId.querySelector('input').addEventListener('change', syncMode);
let files = [];
const fileinput = document.getElementById('fileinput');
const filelist = document.getElementById('filelist');
document.getElementById('filebox').addEventListener('click', ()=> fileinput.click());
fileinput.addEventListener('change', ()=>{
  for(const f of fileinput.files) files.push(f);
  fileinput.value = '';
  renderFiles();
});
function renderFiles(){
  filelist.innerHTML = '';
  let total = 0;
  files.forEach((f,i)=>{
    total += f.size;
    const div = document.createElement('div'); div.className='f';
    div.innerHTML = '<span>📄 '+f.name+' <small style="color:var(--muted)">('+(f.size/1024).toFixed(0)+' KB)</small></span>';
    const b = document.createElement('button'); b.type='button'; b.textContent='✕';
    b.onclick = ()=>{ files.splice(i,1); renderFiles(); };
    div.appendChild(b); filelist.appendChild(div);
  });
  if(total > MAX_TOTAL_BYTES){
    filelist.innerHTML += '<div style="color:var(--danger);font-size:12.5px;margin-top:6px">⚠️ Os anexos excedem 10 MB. Remova algum arquivo.</div>';
  }
}
function fileToB64(file){
  return new Promise((res,rej)=>{
    const r = new FileReader();
    r.onload = ()=> res(r.result.split(',')[1]);
    r.onerror = rej;
    r.readAsDataURL(file);
  });
}
function validate(){
  let ok = true;
  document.querySelectorAll('.field').forEach(f=>f.classList.remove('invalid'));
  [['f-tipo','tipo'],['f-data','data_ocorrencia'],['f-pessoas','pessoas'],['f-desc','descricao']].forEach(([fid,name])=>{
    const el = form.querySelector('[name="'+name+'"]');
    if(!el.value.trim()){ document.getElementById(fid).classList.add('invalid'); ok=false; }
  });
  const consent = document.getElementById('consent');
  document.getElementById('consent-err').style.display = consent.checked ? 'none':'block';
  if(!consent.checked) ok=false;
  let total = files.reduce((s,f)=>s+f.size,0);
  if(total > MAX_TOTAL_BYTES) ok=false;
  return ok;
}
form.addEventListener('submit', async (e)=>{
  e.preventDefault();
  if(!validate()){
    const alvo = document.querySelector('.field.invalid');
    if(alvo) alvo.scrollIntoView({behavior:'smooth',block:'center'});
    return;
  }
  const btn = document.getElementById('btn');
  btn.disabled = true; btn.textContent = 'Enviando com segurança...';
  try{
    const anexos = [];
    for(const f of files){
      anexos.push({ nome:f.name, tipo:f.type || 'application/octet-stream', dados:await fileToB64(f) });
    }
    const fd = new FormData(form);
    const payload = {
      modo: fd.get('modo'),
      nome: fd.get('nome') || '',
      email: fd.get('email') || '',
      telefone: fd.get('telefone') || '',
      cargo: fd.get('cargo') || '',
      tipo: fd.get('tipo'),
      data_ocorrencia: fd.get('data_ocorrencia'),
      local: fd.get('local') || '',
      pessoas: fd.get('pessoas'),
      descricao: fd.get('descricao'),
      anexos: anexos
    };
    const resp = await fetch(ENDPOINT, {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    });
    if(!resp.ok) throw new Error('HTTP '+resp.status);
    const data = await resp.json();
    document.getElementById('proto-code').textContent = data.protocolo || '—';
    form.style.display='none';
    const s = document.getElementById('success');
    s.style.display='block';
    s.scrollIntoView({behavior:'smooth',block:'start'});
  }catch(err){
    btn.disabled=false; btn.textContent='Enviar denúncia com segurança';
    alert('Não foi possível enviar a denúncia agora. Verifique sua conexão e tente novamente.');
  }
});
</script>
</body>
</html>"""
# ===============================================================================


# ---------- Protocolo único e legível (não depende de armazenamento) ----------
def gerar_protocolo():
    """Ex.: MID-20260619-143025  (data + hora, sempre único)."""
    return "MID-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


def esc(v):
    v = (str(v or "").strip()) or "—"
    return (v.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace("\n", "<br>"))

def data_br(iso):
    try:
        return datetime.datetime.strptime(iso, "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return iso or "—"


# ---------- E-mail que REPLICA o formato do formulário ----------
def montar_email(d, protocolo, registrado_em, anexos):
    msg = EmailMessage()
    msg["Subject"] = f"[Canal de Denúncias] {protocolo} — {d.get('tipo','—')}"
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = EMAIL_DESTINO

    anonima = d.get("modo") == "Anônima"
    logo_cid = make_msgid(domain="midrah.com.br")[1:-1]

    def campo(rotulo, valor, opcional=False, area=False):
        tag_opt = ' <span style="color:#64748b;font-weight:500;font-size:12px">(opcional)</span>' if opcional else ''
        minh = 'min-height:54px;' if area else ''
        return f"""
        <div style="margin-bottom:16px">
          <div style="font-size:13px;font-weight:600;color:#33404f;margin-bottom:6px">{rotulo}{tag_opt}</div>
          <div style="padding:11px 14px;border:1px solid #cdd6e2;border-radius:10px;background:#fff;color:#1f2a37;font-size:14.5px;line-height:1.55;{minh}">{esc(valor)}</div>
        </div>"""

    def secao(titulo, desc=""):
        d2 = f'<div style="font-size:13px;color:#64748b;margin:0 0 16px">{desc}</div>' if desc else ''
        return f'<h2 style="font-size:16px;color:#14233D;margin:24px 0 4px;font-weight:700">{titulo}</h2>{d2}'

    if anonima:
        modo_badge = '<span style="background:#fff3cd;color:#8a6d00;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:700">DENÚNCIA ANÔNIMA</span>'
        bloco_ident = (secao("Identificação do denunciante")
            + '<div style="padding:11px 14px;border:1px dashed #cdd6e2;border-radius:10px;background:#fafcfe;color:#64748b;font-size:14px">O denunciante optou por <b>não se identificar</b>.</div>')
    else:
        modo_badge = '<span style="background:#e7f1fb;color:#1577B0;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:700">DENÚNCIA IDENTIFICADA</span>'
        bloco_ident = (secao("Identificação do denunciante", "Informações fornecidas de forma opcional pelo denunciante.")
            + campo("Nome", d.get("nome"), opcional=True)
            + campo("E-mail para contato", d.get("email"), opcional=True)
            + campo("Telefone", d.get("telefone"), opcional=True)
            + campo("Cargo / Setor", d.get("cargo"), opcional=True))

    if anexos:
        itens = "".join(f'<div style="padding:7px 11px;background:#f1f5fa;border:1px solid #e2e8f0;border-radius:8px;margin-top:6px;font-size:13.5px;color:#1f2a37">📄 {esc(a["nome"])} <span style="color:#64748b">({a["bytes_len"]//1024} KB)</span></div>' for a in anexos)
        anexos_html = f'<div style="font-size:13.5px;color:#1f2a37;margin-bottom:6px">{len(anexos)} arquivo(s) anexado(s) a este e-mail:</div>{itens}'
    else:
        anexos_html = '<div style="padding:11px 14px;border:1px dashed #cdd6e2;border-radius:10px;background:#fafcfe;color:#64748b;font-size:14px">Nenhum anexo enviado.</div>'

    html = f"""<!DOCTYPE html><html><body style="margin:0;background:#EEF3F8;padding:24px 0;font-family:'Segoe UI',Arial,sans-serif">
<table cellpadding="0" cellspacing="0" style="max-width:680px;margin:0 auto;width:100%">
 <tr><td>
  <table cellpadding="0" cellspacing="0" style="width:100%;border-radius:14px;overflow:hidden;box-shadow:0 10px 30px rgba(20,35,61,.1)">
   <tr><td style="background:linear-gradient(135deg,#14233D 0%,#0E1B30 45%,#1577B0 130%);padding:30px 32px">
     <img src="cid:{logo_cid}" alt="Midrah" height="28" style="display:block;margin-bottom:16px;filter:brightness(0) invert(1)">
     <div style="color:#fff;font-size:24px;font-weight:700">Canal de Denúncias</div>
     <div style="color:#d6e4f2;font-size:14px;margin-top:6px">Denúncia registrada · Em conformidade com a Lei nº 14.457/2022</div>
   </td></tr>
  </table>
  <table cellpadding="0" cellspacing="0" style="width:100%;background:#fff;border:1px solid #E2E8F0;border-radius:14px;box-shadow:0 10px 30px rgba(20,35,61,.08);margin-top:18px">
   <tr><td style="padding:26px 30px">
     <table cellpadding="0" cellspacing="0" style="width:100%;margin-bottom:6px"><tr>
       <td style="font-size:13px;color:#64748b;vertical-align:top">Protocolo<br><span style="font-size:21px;font-weight:800;color:#14233D;font-family:Consolas,monospace">{protocolo}</span><br><span style="font-size:12px;color:#64748b">Registrado em {registrado_em}</span></td>
       <td style="text-align:right;vertical-align:top">{modo_badge}</td>
     </tr></table>
     {secao("Sobre a ocorrência")}
     {campo("Tipo da ocorrência", d.get("tipo"))}
     {campo("Data da ocorrência", data_br(d.get("data_ocorrencia")))}
     {campo("Local / Setor onde ocorreu", d.get("local"), opcional=True)}
     {campo("Pessoas envolvidas", d.get("pessoas"), area=True)}
     {campo("Descrição dos fatos", d.get("descricao"), area=True)}
     {bloco_ident}
     {secao("Evidências / Anexos")}
     {anexos_html}
     <div style="margin-top:24px;padding:14px 16px;background:#fff7e6;border:1px solid #ffe2a8;border-radius:10px;font-size:12.5px;color:#7a5b00">
       ⚠️ <b>Confidencial.</b> Conteúdo de acesso restrito ao RH e à Diretoria, conforme a Lei nº 14.457/2022 e a LGPD (Lei nº 13.709/2018). Não encaminhe sem necessidade.
     </div>
   </td></tr>
  </table>
  <div style="text-align:center;color:#64748b;font-size:11.5px;margin-top:18px;line-height:1.7">
    Midrah Investimentos · Canal de Denúncias Corporativo<br>
    E-mail gerado automaticamente a partir do formulário.
  </div>
 </td></tr>
</table></body></html>"""

    msg.set_content(
        f"Canal de Denúncias — Protocolo {protocolo} ({registrado_em})\n"
        f"Modo: {d.get('modo','—')}\n\n"
        f"SOBRE A OCORRÊNCIA\n"
        f"Tipo da ocorrência: {d.get('tipo','—')}\n"
        f"Data da ocorrência: {data_br(d.get('data_ocorrencia'))}\n"
        f"Local / Setor: {d.get('local') or '—'}\n"
        f"Pessoas envolvidas: {d.get('pessoas','—')}\n"
        f"Descrição dos fatos: {d.get('descricao','—')}\n\n"
        f"IDENTIFICAÇÃO DO DENUNCIANTE\n"
        f"Nome: {d.get('nome') or '—'}\nE-mail: {d.get('email') or '—'}\n"
        f"Telefone: {d.get('telefone') or '—'}\nCargo/Setor: {d.get('cargo') or '—'}\n"
    )
    msg.add_alternative(html, subtype="html")

    # logo inline (a partir do base64 embutido)
    try:
        logo_bytes = base64.b64decode(LOGO_B64)
        msg.get_payload()[1].add_related(logo_bytes, maintype="image", subtype="png", cid=f"<{logo_cid}>")
    except Exception:
        pass

    for a in anexos:
        ctype = a.get("tipo") or mimetypes.guess_type(a["nome"])[0] or "application/octet-stream"
        maintype, _, subtype = ctype.partition("/")
        msg.add_attachment(a["bytes"], maintype=maintype or "application",
                           subtype=subtype or "octet-stream", filename=a["nome"])
    return msg


def enviar_email(msg, protocolo):
    if SMTP_HOST and SMTP_USER and SMTP_PASS:
        ctx = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as s:
            s.starttls(context=ctx)
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
        print(f"   [OK] E-mail enviado para {EMAIL_DESTINO}")
        return
    os.makedirs(PEND_DIR, exist_ok=True)
    with open(os.path.join(PEND_DIR, f"{protocolo}.eml"), "wb") as f:
        f.write(bytes(msg))
    print(f"   [!] SMTP não configurado — e-mail salvo em emails_pendentes/{protocolo}.eml")


def processar(d):
    with _lock:
        protocolo = gerar_protocolo()
        registrado_em = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        anexos = []
        for a in (d.get("anexos") or []):
            try:
                raw = base64.b64decode(a.get("dados", ""))
            except Exception:
                continue
            anexos.append({"nome": a.get("nome", "anexo"), "tipo": a.get("tipo", ""),
                           "bytes": raw, "bytes_len": len(raw)})
        msg = montar_email(d, protocolo, registrado_em, anexos)
        try:
            enviar_email(msg, protocolo)
        except Exception as e:
            os.makedirs(PEND_DIR, exist_ok=True)
            with open(os.path.join(PEND_DIR, f"{protocolo}.eml"), "wb") as f:
                f.write(bytes(msg))
            print(f"   [ERRO] Falha no envio ({e}); e-mail salvo em emails_pendentes/{protocolo}.eml")
        print(f"   Protocolo {protocolo} registrado.")
        return protocolo


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/", "/index.html"):
            page = HTML_PAGE.replace("midrah-logo.png", LOGO_DATA_URI)
            return self._send(200, page, "text/html; charset=utf-8")
        self._send(404, b'{"erro":"nao encontrado"}')

    def do_POST(self):
        if self.path.split("?")[0] != "/enviar":
            return self._send(404, b'{"erro":"nao encontrado"}')
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length > 20 * 1024 * 1024:
                return self._send(413, b'{"erro":"payload muito grande"}')
            d = json.loads(self.rfile.read(length).decode("utf-8"))
            for campo_obr in ("tipo", "data_ocorrencia", "pessoas", "descricao"):
                if not str(d.get(campo_obr, "")).strip():
                    return self._send(400, json.dumps({"erro": f"campo obrigatório: {campo_obr}"}).encode())
            protocolo = processar(d)
            self._send(200, json.dumps({"ok": True, "protocolo": protocolo}).encode())
        except Exception as e:
            print("ERRO:", e)
            self._send(500, json.dumps({"erro": "falha ao processar"}).encode())


def main():
    os.makedirs(PEND_DIR, exist_ok=True)
    print("=" * 56)
    print("  Canal de Denúncias — Midrah Investimentos")
    print("=" * 56)
    print(f"  Servidor no ar:  http://localhost:{PORT}")
    print(f"  Destino e-mail:  {EMAIL_DESTINO}")
    print(f"  Remetente SMTP:  {SMTP_USER}")
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS):
        print("  AVISO: SMTP não configurado — e-mails serão salvos em emails_pendentes/")
    print("  (Pressione Ctrl+C para encerrar)")
    print("=" * 56)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
