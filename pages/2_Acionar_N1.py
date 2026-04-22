import streamlit as st

st.set_page_config(page_title="Acionar N1", layout="wide")

c1, c2 = st.columns(2, gap="large")

c1.title("Acionar N1")

mensagem = c1.text_area("Cole a mensagem com o número aqui:", height=200)

if c1.button("Acionar escola", type="primary"):
    c1.write("Acionando...")

c2.title("Escolas Acionadas")
c2.subheader("Aqui vai as escolas...")