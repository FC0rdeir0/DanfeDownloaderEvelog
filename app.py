from pathlib import Path
import pandas as pd
import streamlit as st

from automacao import carregar_credenciais, buscar_chaves
from meudanfe import carregar_config_api, baixar_danfes

BASE_DIR = Path(__file__).resolve().parent
LOGIN_FILE = BASE_DIR / "login.xlsx"
RESULTADOS_DIR = BASE_DIR / "resultados"

st.set_page_config(layout="wide")
st.title("DanfeDownloader Evelog")

col_1, _ = st.columns([1, 2])

with col_1:
    arquivo = st.file_uploader("Planilha de coletas", type=["xlsx", "xls"])

if arquivo is not None:
    try:
        df = pd.read_excel(arquivo, skiprows=1)
        df = df.iloc[:, [0]].copy()
        df.columns = ["pedido"]
        df = df[df["pedido"].notna()].reset_index(drop=True)

        with col_1:
            st.info(f"{len(df)} pedido(s) encontrado(s).")

    except Exception as exc:
        with col_1:
            st.error(f"Não foi possível ler a planilha: {exc}")
        st.stop()
    
    with col_1:
        clicou_baixar = st.button("Baixar DANFEs", type="primary", use_container_width=True)

    # Log abaixo do botão. Usamos session_state para o conteúdo não desaparecer
    # quando o Streamlit fizer um novo rerun da página.
    if clicou_baixar:
        st.session_state["logs"] = []

    if "logs" not in st.session_state:
        st.session_state["logs"] = []

    with st.expander("Log da execução", expanded=False):
        log_area = st.empty()
        if st.session_state["logs"]:
            log_area.code("\n".join(st.session_state["logs"]), language=None)

    def registrar(msg):
        st.session_state["logs"].append(msg)
        log_area.code("\n".join(st.session_state["logs"]), language=None)

    if clicou_baixar:
        if not LOGIN_FILE.exists():
            st.error("Arquivo login.xlsx não encontrado na pasta do programa.")
            st.stop()

        try:
            from datetime import datetime

            agora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            pasta_resultado = RESULTADOS_DIR / f"danfes_{agora}"
            pasta_resultado.mkdir(parents=True, exist_ok=True)

            usuario, senha = carregar_credenciais(LOGIN_FILE)
            api_key, api_base_url = carregar_config_api(LOGIN_FILE)

            with st.spinner("Buscando chaves no FractionWeb..."):
                resultado = buscar_chaves(df, usuario, senha, registrar)

            with st.spinner("Consultando e baixando DANFEs..."):
                resultado = baixar_danfes(
                    resultado,
                    api_key,
                    api_base_url,
                    pasta=pasta_resultado,
                    log=registrar,
                )

            st.session_state["resultado"] = resultado
            st.session_state["pasta_resultado"] = str(pasta_resultado)
            registrar(f"📁 Arquivos salvos em: {pasta_resultado}")
            registrar("🏁 Processo finalizado.")

        except Exception as exc:
            registrar(f"❌ Erro geral: {exc}")
            st.error(str(exc))

if "resultado" in st.session_state:
    resultado = st.session_state["resultado"]
    st.subheader("Resultado final")
    st.dataframe(resultado, use_container_width=True, hide_index=True)

    pasta_resultado = st.session_state.get("pasta_resultado")
    if pasta_resultado:
        st.success(f"DANFEs salvos em: {pasta_resultado}")
