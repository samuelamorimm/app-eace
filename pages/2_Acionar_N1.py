import streamlit as st
import re
from urllib.parse import quote #codificar mensagem do link

st.set_page_config(page_title="Acionar N1", layout="wide")
c1, c2 = st.columns(2, gap="large")

if 'feedback' not in st.session_state:
    st.session_state['feedback'] = None

if 'acionadas' not in st.session_state:
    st.session_state['acionadas'] = []

if 'link_whatsapp' not in st.session_state:
    st.session_state['link_whatsapp'] = None

if st.session_state['feedback']:
    tipo, msg = st.session_state['feedback']
    if tipo == 'success':
        c1.success(msg)
    else:
        c1.error(msg)

def parse_mensagem(texto): #função para captar dados das mensagens
    dados = {}

    inep_m = re.search(r'- (\d{8})', texto)
    escola_m = re.search(r'escola (.+?) -', texto)

    primeira_linha = texto.strip().split('\n')[0] #pega a primeira linha da mensagem onde ta o número
    numero_m = re.sub(r'\D', '', primeira_linha) #limpa o número mantendo apenas digitos

    dados['inep'] = inep_m.group(1) if inep_m else None
    dados['escola'] = escola_m.group(1) if escola_m else None
    dados['numero'] = numero_m if numero_m else None

    return dados



c1.title("Acionar N1")

mensagem = c1.text_area("Cole a mensagem com o número aqui:", height=200)

if c1.button("Acionar escola", type="primary"): #botão para acionar escolas
    dados = parse_mensagem(mensagem)

    texto_acionamento = f"Olá, meu nome é Samuel Amorim, faço parte do projeto EACE. Estou entrando em contato sobre a escola {dados['escola']} - {dados['inep']}. Pode nos informar o que está acontecendo com a rede?"

    link = f"https://wa.me/{dados['numero']}?text={quote(texto_acionamento)}"

    st.session_state['link_whatsapp'] = link

    #verificando se inep já foi acionado
    ineps_ja_adicionados = [e['inep'] for e in st.session_state['acionadas']]
    if dados['inep'] not in ineps_ja_adicionados:
        st.session_state['acionadas'].append(dados)
        st.session_state['feedback'] = ('success', f"Escola {dados['escola']} - {dados['inep']} acionada com sucesso!")
    else:
        st.session_state['feedback'] = ('error', f"Escola {dados['escola']} - {dados['inep']} já foi acionada!")
    
    st.rerun()  # força reexecução imediata

if st.session_state['link_whatsapp']:
        c1.link_button("Abrir WhatsApp", st.session_state['link_whatsapp']) #ir para o whatsapp com a mensagem pronta

c2.title("Escolas Acionadas")
for escola in st.session_state['acionadas']:
    
    col1, col2 = c2.columns([2, 1])
    col1.markdown(f"**INEP: {escola['inep']}**")
    col1.caption(f"🏫 {escola['escola']} | 📞 {escola['numero']}")
    col2.selectbox(
        "Status",
        [ "Acionado", "Pendente", "Sem contato"],
        key=f"status_{escola['inep']}"
    )