@echo off
setlocal
cd /d "%~dp0"

title Downloader de DANFEs

echo ==========================================
echo        DOWNLOADER DE DANFES
echo ==========================================
echo.

rem ==================================================
rem 1. Verifica o Python
rem ==================================================

where python >nul 2>&1

if errorlevel 1 (
    echo ERRO: Python nao foi encontrado.
    echo.
    echo Instale o Python e marque a opcao:
    echo Add Python to PATH
    echo.
    pause
    exit /b 1
)

rem ==================================================
rem 2. Verifica o Git
rem ==================================================

where git >nul 2>&1

if errorlevel 1 (
    echo AVISO: Git nao foi encontrado.
    echo O aplicativo sera iniciado sem procurar atualizacoes.
    echo.
    goto INSTALAR_AMBIENTE
)

rem ==================================================
rem 3. Verifica se e repositorio Git
rem ==================================================

if not exist ".git" (
    echo AVISO: Esta pasta nao e um repositorio Git.
    echo O aplicativo sera iniciado sem procurar atualizacoes.
    echo.
    goto INSTALAR_AMBIENTE
)

rem ==================================================
rem 4. Atualiza o projeto pelo GitHub
rem ==================================================

echo Verificando atualizacoes no GitHub...
echo.

git pull --ff-only

if errorlevel 1 (
    echo.
    echo AVISO: Nao foi possivel atualizar o projeto.
    echo.
    echo Possiveis motivos:
    echo - existem alteracoes locais;
    echo - computador sem internet;
    echo - acesso ao repositorio expirou;
    echo - branch local diferente da remota.
    echo.
    echo O aplicativo sera iniciado com a versao atual.
    echo.
) else (
    echo.
    echo Projeto atualizado com sucesso.
    echo.
)

:INSTALAR_AMBIENTE

rem ==================================================
rem 5. Cria ambiente virtual
rem ==================================================

if not exist ".venv\Scripts\python.exe" (
    echo Criando ambiente virtual...
    echo.

    python -m venv .venv

    if errorlevel 1 (
        echo.
        echo ERRO: Nao foi possivel criar o ambiente virtual.
        pause
        exit /b 1
    )

    echo Ambiente virtual criado.
    echo.
)

set "PYTHON=.venv\Scripts\python.exe"

rem ==================================================
rem 6. Verifica requirements.txt
rem ==================================================

if not exist "requirements.txt" (
    echo ERRO: requirements.txt nao foi encontrado.
    pause
    exit /b 1
)

rem ==================================================
rem 7. Atualiza pip
rem ==================================================

echo Verificando pip...

"%PYTHON%" -m pip install --upgrade pip --quiet

if errorlevel 1 (
    echo.
    echo ERRO: Nao foi possivel atualizar o pip.
    pause
    exit /b 1
)

rem ==================================================
rem 8. Instala / atualiza dependencias
rem ==================================================

echo Verificando dependencias...

"%PYTHON%" -m pip install -r requirements.txt --quiet

if errorlevel 1 (
    echo.
    echo ERRO: Nao foi possivel instalar as dependencias.
    pause
    exit /b 1
)

echo Dependencias verificadas.
echo.

rem ==================================================
rem 9. Instala / verifica Chromium do Playwright
rem ==================================================

echo Verificando Chromium do Playwright...

"%PYTHON%" -m playwright install chromium

if errorlevel 1 (
    echo.
    echo ERRO: Nao foi possivel instalar o Chromium.
    pause
    exit /b 1
)

echo Chromium verificado.
echo.

rem ==================================================
rem 10. Cria pastas locais
rem ==================================================

if not exist "resultados" mkdir resultados
if not exist "perfil_real" mkdir perfil_real

rem ==================================================
rem 11. Verifica arquivos essenciais
rem ==================================================

if not exist "app.py" (
    echo ERRO: app.py nao foi encontrado.
    pause
    exit /b 1
)

if not exist "automacao.py" (
    echo ERRO: automacao.py nao foi encontrado.
    pause
    exit /b 1
)

if not exist "meudanfe.py" (
    echo ERRO: meudanfe.py nao foi encontrado.
    pause
    exit /b 1
)

if not exist "login.xlsx" (
    echo ERRO: login.xlsx nao foi encontrado.
    echo.
    echo O arquivo login.xlsx deve conter:
    echo USER
    echo PASSWORD
    echo API_KEY
    echo.
    pause
    exit /b 1
)

rem ==================================================
rem 12. Inicia Streamlit
rem ==================================================

echo ==========================================
echo Iniciando o Downloader de DANFEs...
echo ==========================================
echo.
echo Para encerrar, pressione Ctrl+C.
echo.

"%PYTHON%" -m streamlit run app.py

echo.
echo Aplicativo encerrado.
pause

endlocal