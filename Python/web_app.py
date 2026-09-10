import streamlit as st
import os
import sys
import shutil
import subprocess
from pathlib import Path

st.set_page_config(
    page_title="Contextual QnA Extractor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados en CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #38BDF8;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1rem;
        color: #94A3B8;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #10B981;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        height: 3rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">⚡ Contextual QnA Extractor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Interfaz Web Interactiva RAG Multi-Agente con Ollama & LangGraph</div>', unsafe_allow_html=True)

BASE_DIR = Path(__file__).resolve().parents[1]
INPUTS_DIR = BASE_DIR / "inputs"
OUTPUTS_DIR = BASE_DIR / "outputs" / "cuestionarios-logs"

INPUTS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# Sidebar - Configuración
st.sidebar.header("⚙️ Configuración del RAG")
profile = st.sidebar.selectbox(
    "Perfil del Evaluado",
    ["estudiante universitario", "técnico avanzado", "principiante", "estudiante secundario"]
)

model_name = st.sidebar.selectbox(
    "Modelo LLM (Ollama)",
    ["gemma4:e2b", "llama3.1", "gemma2", "mistral"]
)

top_n = st.sidebar.slider("Número de preguntas", min_value=1, max_value=10, value=5)

# Main area - Upload
st.subheader("1. Cargar Archivo de Entrada")
uploaded_file = st.file_uploader(
    "Arrastra o selecciona cualquier archivo de estudio (PDF, Word, Markdown, Texto, Imágenes WEBP/PNG)",
    type=["pdf", "docx", "doc", "txt", "md", "webp", "png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    file_path = INPUTS_DIR / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success(f"✅ Archivo cargado correctamente: `{uploaded_file.name}`")
    
    if st.button("🚀 GENERAR CUESTIONARIO CON RAG"):
        with st.spinner(f"Ejecutando pipeline RAG con {model_name}..."):
            cmd = [
                sys.executable,
                str(BASE_DIR / "Python" / "main.py"),
                "--input", uploaded_file.name,
                "--perfil", profile,
                "--modelo", model_name,
                "--top_n", str(top_n)
            ]
            
            env = os.environ.copy()
            env["PYTHONPATH"] = str(BASE_DIR / "python") + ":" + str(BASE_DIR / "Python")
            
            res = subprocess.run(cmd, cwd=str(BASE_DIR), capture_output=True, text=True, env=env)
            
            st.code(res.stdout, language="bash")
            
            if res.returncode == 0:
                st.balloons()
                st.success("¡Proceso completado con éxito!")
                
                base_stem = Path(uploaded_file.name).stem
                out_file = OUTPUTS_DIR / f"cuestionario_{base_stem}.md"
                out_json = BASE_DIR / "outputs" / "cuestionario_gemma.json"
                
                if out_file.exists():
                    st.subheader("📄 Cuestionario Generado (Markdown)")
                    content = out_file.read_text(encoding="utf-8")
                    st.markdown(content)
                    st.download_button("⬇️ Descargar Cuestionario (.md)", content, file_name=f"cuestionario_{base_stem}.md")
                elif out_json.exists():
                    st.subheader("📄 Cuestionario Generado (JSON)")
                    content = out_json.read_text(encoding="utf-8")
                    st.json(content)
            else:
                st.error("Error al ejecutar el pipeline RAG:")
                st.code(res.stderr)
