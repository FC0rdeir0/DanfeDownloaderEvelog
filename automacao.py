from pathlib import Path
import re
import pandas as pd
from playwright.sync_api import sync_playwright

LOGIN_URL = "https://jadlog.com.br/FractionWeb/login.jad?state=invalid"


def carregar_credenciais(caminho="login.xlsx"):
    cred = pd.read_excel(caminho)
    return str(cred.loc[0, "USER"]), str(cred.loc[0, "PASSWORD"])


def buscar_chaves(df: pd.DataFrame, usuario: str, senha: str, log=lambda msg: None) -> pd.DataFrame:
    resultado = df.copy()
    resultado["chave_nfe"] = ""
    resultado["status_fraction"] = "PENDENTE"
    resultado["status_danfe"] = "PENDENTE"
    resultado["mensagem"] = ""

    perfil = Path(__file__).resolve().parent / "perfil_real"

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(perfil),
            headless=True,
            slow_mo=200,
        )
        page = context.pages[0] if context.pages else context.new_page()

        try:
            log("🔐 Fazendo login no FractionWeb...")
            page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=60000)
            page.fill("input[name='id_usuario']", usuario)
            page.fill("input[name='id_senha']", senha)
            page.click("input[type='submit']")
            page.wait_for_load_state("networkidle", timeout=60000)

            try:
                page.get_by_role("button", name="Close").first.click(timeout=5000)
            except Exception:
                pass

            log("✅ Login realizado.")

            for index, row in resultado.iterrows():
                pedido = str(row["pedido"]).strip()
                if not pedido or pedido.lower() == "nan":
                    resultado.at[index, "status_fraction"] = "PULADO"
                    resultado.at[index, "status_danfe"] = "PULADO"
                    resultado.at[index, "mensagem"] = "Pedido vazio"
                    continue

                try:
                    log(f"📦 {pedido}: buscando chave da NF-e...")
                    page.get_by_role("link", name="Consultas").click(timeout=15000)
                    page.get_by_role("link", name="Pesquisar").click(timeout=15000)
                    page.wait_for_load_state("networkidle", timeout=60000)

                    campo = page.get_by_role("textbox").first
                    campo.fill("")
                    campo.fill(pedido)
                    page.get_by_role("button", name="Processar").click()

                    toggler = page.locator(".ui-tree-toggler").first
                    toggler.wait_for(timeout=15000)
                    toggler.click()

                    item_nf = page.get_by_role("treeitem").filter(has_text="NFe:").last
                    item_nf.wait_for(timeout=15000)
                    match = re.search(r"\d{44}", item_nf.inner_text())
                    if not match:
                        raise RuntimeError("Chave de 44 dígitos não encontrada")

                    chave = match.group()
                    resultado.at[index, "chave_nfe"] = chave
                    resultado.at[index, "status_fraction"] = "OK"
                    resultado.at[index, "mensagem"] = "Chave encontrada"
                    log(f"✅ {pedido}: {chave}")

                except Exception as exc:
                    resultado.at[index, "status_fraction"] = "ERRO"
                    resultado.at[index, "status_danfe"] = "PULADO"
                    resultado.at[index, "mensagem"] = f"FractionWeb: {exc}"
                    log(f"❌ {pedido}: erro no FractionWeb — {exc}")
        finally:
            context.close()

    return resultado
