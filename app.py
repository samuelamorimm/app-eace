import streamlit as st
import re

st.set_page_config(page_title="APP Eace", layout="centered")
st.title("Agrupador de Massivas")



lista_sites = st.text_area("Cole a lista de sites DONW aqui:", height=200)

#percorrer blocos de sites filtrando infos
def parse_sites(texto):
    #separa blocos de sites =============================
    blocos = re.split(r'(?=🔴 \[SITE DOWN\])', texto)

    #verifica grupos vazios ===================================
    blocos = [item.strip() for item in blocos if item.strip()]
    sites = []

    for bloco in blocos:
        site = {}
        inep_m = re.search(r'\((\d{8})\)', bloco)
        uf_m = re.search(r'\[SITE DOWN\] ([A-Z]{2})', bloco)
        municipio = re.search(r'\[SITE DOWN\] [A-Z]{2} (.+?) \(', bloco)
        provedor = re.search(r'Provedor: (.+?)\n', bloco)
        tempo_off = re.search(r'Tempo Parado: (.+?)\n', bloco)
        
        site['inep'] = inep_m.group(1) if inep_m else None
        site['uf'] = uf_m.group(1) if uf_m else None
        site['municipio'] = municipio.group(1) if municipio else None
        site['provedor'] = provedor.group(1) if provedor else None
        site['tempo_off'] = tempo_off.group(1) if tempo_off else None

        tempo_off_min = parse_minutes(site['tempo_off'])
        site['tempo_off_min'] = int(tempo_off_min)

        sites.append(site)
    
    return sites

#função que converte o tempo para minutos
def parse_minutes(texto):
    if not texto:
        return None
    
    #dias
    d = re.search(r'(\d+)d', texto)
    d = int(d.group(1)) if d else 0

    #horas
    h = re.search(r'(\d+)h', texto)
    h = int(h.group(1)) if h else 0

    #minutos
    m = re.search(r'(\d+)m', texto)
    m = int(m.group(1)) if m else 0

    min = d * 1440 + h * 60 + m
    return min

def agrupar(sites):
    usados = []
    grupos = []

    for i in range(len(sites)): # pega o indice
        if i in usados: #verifica se está em usados
            continue

        grupo = [sites[i]] # cria um grupo com o site da vez

        for j in range(i + 1, len(sites)): #aqui ocorre a comparação, vai comparar o restante com o site da vez
            if j in usados: #se j já estiver em usados pula e compara o próximo
                continue
            
            mesma_uf = sites[i]['uf'] == sites[j]['uf']
            mesma_cidade = sites[i]['municipio'] == sites[j]['municipio']
            minutos = abs(sites[i]['tempo_off_min'] - sites[j]['tempo_off_min']) <= 10

            if mesma_cidade and mesma_uf and minutos: #se a comparação der certo adiciona o site j ao grupo do site i
                grupo.append(sites[j]) # aqui adiciona o site j ao grupo do site i
                usados.append(j) # aqui adciona o site j em usados, pois ele já faz parte de um grupo

        #adiciona i em usados e grupo tratado nos grupos e vai comparar o próximo site
        usados.append(i) 
        grupos.append(grupo)
    
    return grupos # ao final do processo retorna os grupos



#processamento de massivas
if st.button("Processar", type="primary"):
    grupos = agrupar(parse_sites(lista_sites))
    massivas = [grupo for grupo in grupos if len(grupo) >= 3] # se o grupo de sites em grupos for maior ou = 3 sites, adiciona nas massivas
    pares = [grupo for grupo in grupos if len(grupo) == 2] # se o grupo de sites em grupos for = 2 sites, adiciona nos pares
    individuais = [grupo for grupo in grupos if len(grupo) == 1] # sites sem grupo
    nao_massivas = pares + individuais

    st.markdown("""
    <style>
    [data-testid="stMetric"] {
        background-color: #1e1e2e;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #333;
    }
    </style>
    """, unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Massivas", len(massivas))
    c2.metric("Pares", len(pares))
    c3.metric("Individuais", len(individuais))

    #Card para exibir massivas
    st.subheader("Massivas")
    with st.expander(f"Massivas"):
        for grupo in massivas: # percorre os grupos de massivas
            mestre = grupo[0]
            filhos = grupo[1:]
            with st.expander(f"INEP Mestre: {mestre['inep']}"):
                nota = "POSSÍVEL MASSIVA\nINEPS AFETADOS:\n"
                nota += "\n".join([filho['inep'] for filho in filhos]) #junta os filhos na nota com .join colocando quebra de linhas
                st.code(nota)

    st.subheader("Abrir Chamado")
    with st.expander("Abrir Chamado"):
        for grupo in nao_massivas:
            for site in grupo:
                st.write("INEP")
                st.code(site['inep'])
                
    