from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from automacao import buscar_chaves
from meudanfe import baixar_danfes

BASE_DIR = Path(__file__).resolve().parent
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
        clicou_baixar = st.button(
            "Baixar DANFEs",
            type="primary",
            use_container_width=True,
        )

    # Log abaixo do botão. O session_state mantém o conteúdo nos reruns do Streamlit.
    if clicou_baixar:
        st.session_state["logs"] = []
        st.session_state.pop("resultado", None)
        st.session_state.pop("pasta_resultado", None)

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
        try:
            agora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            pasta_resultado = RESULTADOS_DIR / f"danfes_{agora}"
            pasta_resultado.mkdir(parents=True, exist_ok=True)

            with st.spinner("Buscando chaves no FractionWeb..."):
                resultado = buscar_chaves(df, log=registrar)

            with st.spinner("Consultando e baixando DANFEs..."):
                resultado = baixar_danfes(
                    resultado,
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
