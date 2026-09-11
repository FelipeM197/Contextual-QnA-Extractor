#!/usr/bin/env python3
"""
Interfaz Gráfica (GUI) para Contextual-QnA-Extractor
Permite seleccionar cualquier archivo (PDF, DOCX, TXT, MD, WEBP, PNG, etc.),
configurar los parámetros del RAG y ejecutar el pipeline sin editar código.
"""

import sys
import os
import shutil
import subprocess
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

# Configuración del tema CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class QnAGuiApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Contextual QnA Extractor - Interfaz Gráfica")
        self.geometry("900 x 720")
        self.minsize(800, 600)

        self.project_dir = Path(__file__).resolve().parents[1]
        self.inputs_dir = self.project_dir / "inputs"
        self.outputs_dir = self.project_dir / "outputs" / "cuestionarios-logs"
        
        self.inputs_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)

        self.selected_file_path = None
        
        self._build_ui()

    def _build_ui(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=10)
        header_frame.pack(fill="x", padx=15, pady=10)

        title_label = ctk.CTkLabel(
            header_frame, 
            text="⚡ Contextual QnA Extractor", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#38BDF8"
        )
        title_label.pack(side="left", padx=15, pady=12)

        sub_label = ctk.CTkLabel(
            header_frame, 
            text="Generador RAG Multi-Agente con Ollama & LangGraph", 
            font=ctk.CTkFont(size=12),
            text_color="#94A3B8"
        )
        sub_label.pack(side="right", padx=15, pady=12)

        # Main content container
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=5)

        # Left Column: Inputs & Parameters
        left_col = ctk.CTkFrame(content_frame, width=380, fg_color="#0F172A", corner_radius=10)
        left_col.pack(side="left", fill="both", padx=(0, 10), pady=5)

        # Section 1: File Selection
        file_section_title = ctk.CTkLabel(
            left_col, text="1. Seleccionar Archivo de Entrada", 
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#E2E8F0"
        )
        file_section_title.pack(anchor="w", padx=15, pady=(15, 5))

        file_btn = ctk.CTkButton(
            left_col, 
            text="📁 Buscar Archivo (PDF, DOCX, TXT, MD, IMAGEN)",
            command=self._select_file,
            fg_color="#3B82F6",
            hover_color="#2563EB"
        )
        file_btn.pack(fill="x", padx=15, pady=8)

        self.file_label = ctk.CTkLabel(
            left_col, 
            text="Ningún archivo seleccionado...", 
            font=ctk.CTkFont(size=11, slant="italic"), 
            text_color="#64748B",
            wraplength=340
        )
        self.file_label.pack(anchor="w", padx=15, pady=(0, 10))

        # Divider
        ctk.CTkFrame(left_col, height=1, fg_color="#334155").pack(fill="x", padx=15, pady=5)

        # Section 2: Parameters
        params_title = ctk.CTkLabel(
            left_col, text="2. Parámetros del Sistema", 
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#E2E8F0"
        )
        params_title.pack(anchor="w", padx=15, pady=(10, 5))

        # Perfil de usuario
        ctk.CTkLabel(left_col, text="Perfil del Evaluado:", font=ctk.CTkFont(size=12), text_color="#CBD5E1").pack(anchor="w", padx=15, pady=(5, 2))
        self.profile_entry = ctk.CTkEntry(
            left_col, 
            placeholder_text="Ej: estudiante universitario"
        )
        self.profile_entry.insert(0, "estudiante universitario")
        self.profile_entry.pack(fill="x", padx=15, pady=(0, 8))

        # Modelo LLM
        ctk.CTkLabel(left_col, text="Modelo Ollama LLM:", font=ctk.CTkFont(size=12), text_color="#CBD5E1").pack(anchor="w", padx=15, pady=(5, 2))
        self.model_combo = ctk.CTkComboBox(
            left_col, 
            values=["gemma4:e2b", "llama3.1", "gemma2", "mistral"]
        )
        self.model_combo.set("gemma4:e2b")
        self.model_combo.pack(fill="x", padx=15, pady=(0, 8))

        # Número de preguntas
        ctk.CTkLabel(left_col, text="Número de Preguntas:", font=ctk.CTkFont(size=12), text_color="#CBD5E1").pack(anchor="w", padx=15, pady=(5, 2))
        self.questions_entry = ctk.CTkEntry(
            left_col, 
            placeholder_text="Ej: 5"
        )
        self.questions_entry.insert(0, "5")
        self.questions_entry.pack(fill="x", padx=15, pady=(0, 15))

        # Action Button
        self.run_btn = ctk.CTkButton(
            left_col, 
            text="🚀 GENERAR CUESTIONARIO",
            command=self._start_generation_thread,
            fg_color="#10B981",
            hover_color="#059669",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        self.run_btn.pack(fill="x", padx=15, pady=(10, 15))

        # Right Column: Output Log & Result View
        right_col = ctk.CTkFrame(content_frame, fg_color="#0F172A", corner_radius=10)
        right_col.pack(side="right", fill="both", expand=True, pady=5)

        right_title = ctk.CTkLabel(
            right_col, text="Consola de Salida & Resultado", 
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#E2E8F0"
        )
        right_title.pack(anchor="w", padx=15, pady=(15, 5))

        self.log_textbox = ctk.CTkTextbox(
            right_col, 
            font=ctk.CTkFont(family="monospace", size=11),
            fg_color="#020617",
            text_color="#38BDF8"
        )
        self.log_textbox.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # Bottom Bar
        bottom_frame = ctk.CTkFrame(right_col, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=15, pady=(0, 15))

        open_folder_btn = ctk.CTkButton(
            bottom_frame, 
            text="📂 Abrir Carpeta de Logs", 
            command=self._open_outputs_folder,
            fg_color="#475569",
            hover_color="#334155",
            width=180
        )
        open_folder_btn.pack(side="left")

        self.status_label = ctk.CTkLabel(
            bottom_frame, 
            text="Estado: Listo", 
            font=ctk.CTkFont(size=12),
            text_color="#10B981"
        )
        self.status_label.pack(side="right")

    def _select_file(self):
        filetypes = [
            ("Todos los archivos compatibles", "*.pdf *.docx *.doc *.txt *.md *.webp *.png *.jpg *.jpeg"),
            ("Archivos PDF", "*.pdf"),
            ("Documentos Word", "*.docx *.doc"),
            ("Archivos de Texto / Markdown", "*.txt *.md"),
            ("Imágenes", "*.webp *.png *.jpg *.jpeg"),
            ("Todos los archivos", "*.*")
        ]
        
        path = filedialog.askopenfilename(title="Seleccionar archivo para QnA", filetypes=filetypes)
        if path:
            self.selected_file_path = Path(path)
            self.file_label.configure(text=f"📌 {self.selected_file_path.name}", text_color="#38BDF8")
            self._log(f"[INFO] Archivo seleccionado: {self.selected_file_path}")

    def _log(self, text: str):
        self.after(0, self._append_log, text)

    def _append_log(self, text: str):
        if text.strip():
            self.log_textbox.insert("end", text + "\n")
            self.log_textbox.see("end")

    def _set_status(self, text: str, color: str):
        self.after(0, lambda: self.status_label.configure(text=text, text_color=color))

    def _set_btn(self, state: str, text: str):
        self.after(0, lambda: self.run_btn.configure(state=state, text=text))

    def _open_outputs_folder(self):
        folder = str(self.outputs_dir)
        if sys.platform == "win32":
            os.startfile(folder)
        elif sys.platform == "darwin":
            subprocess.run(["open", folder])
        else:
            subprocess.run(["xdg-open", folder])

    def _ensure_phoenix_running(self):
        import urllib.request
        import time
        try:
            urllib.request.urlopen("http://127.0.0.1:6006/", timeout=1)
            self._log("[INFO] Servidor Phoenix ya está corriendo en el puerto 6006.")
            return
        except Exception:
            self._log("[INFO] Iniciando servidor Arize Phoenix automáticamente...")
            
        if sys.platform == "win32":
            script_path = self.project_dir / "sh" / "iniciar_phoenix.ps1"
            cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_path)]
            subprocess.Popen(
                cmd,
                cwd=str(self.project_dir),
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            script_path = self.project_dir / "sh" / "iniciar_phoenix.sh"
            cmd = ["bash", str(script_path)]
            subprocess.Popen(
                cmd,
                cwd=str(self.project_dir),
                start_new_session=True
            )
            
        self._log("[INFO] Esperando a que el servidor Phoenix responda (puede tardar unos segundos)...")
        for _ in range(15):
            time.sleep(1)
            try:
                urllib.request.urlopen("http://127.0.0.1:6006/", timeout=1)
                self._log("[INFO] ¡Servidor Phoenix iniciado exitosamente en una nueva ventana!")
                return
            except Exception:
                pass
        self._log("[WARNING] No se pudo confirmar que Phoenix inició a tiempo. Las trazas iniciales podrían perderse.")

    def _check_model_available(self, model_name: str) -> bool:
        ollama = shutil.which("ollama")
        if not ollama:
            return False
            
        env = os.environ.copy()
        if sys.platform == "win32" and Path("D:/").exists():
            env["OLLAMA_MODELS"] = r"d:\Ollama_Modelos"
            
        try:
            flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            resultado = subprocess.run(
                [ollama, "list"], capture_output=True, text=True, check=False, env=env, creationflags=flags
            )
            return any(line.startswith(model_name) for line in resultado.stdout.splitlines())
        except Exception:
            return False

    def _start_generation_thread(self):
        if not self.selected_file_path:
            messagebox.showwarning("Atención", "Por favor selecciona un archivo primero.")
            return

        model = self.model_combo.get()
        if not self._check_model_available(model):
            proceed = messagebox.askyesno(
                "Modelo no encontrado",
                f"El modelo '{model}' no está disponible localmente.\n\n"
                "El sistema entrará en MODO FALLBACK (búsqueda básica y extracción de texto crudo sin generación de IA).\n\n"
                "¿Deseas continuar de todas formas?"
            )
            if not proceed:
                return

        self.run_btn.configure(state="disabled", text="⏳ Procesando...")
        self.status_label.configure(text="Estado: Ejecutando RAG...", text_color="#F59E0B")
        
        thread = threading.Thread(target=self._run_generation, daemon=True)
        thread.start()

    def _run_generation(self):
        try:
            # 1. Copiar el archivo a inputs/ si no está ahí
            target_input_path = self.inputs_dir / self.selected_file_path.name
            if self.selected_file_path.resolve() != target_input_path.resolve():
                shutil.copy2(self.selected_file_path, target_input_path)
                self._log(f"[INFO] Copiado archivo a inputs/{self.selected_file_path.name}")

            input_filename = self.selected_file_path.name
            profile = self.profile_entry.get()
            model = self.model_combo.get()
            top_n = self.questions_entry.get()

            self._log(f"\n=============================================")
            self._log(f" Ejecutando Sistema QnA RAG Multi-Agente")
            self._log(f" Archivo : {input_filename}")
            self._log(f" Perfil  : {profile}")
            self._log(f" Modelo  : {model}")
            self._log(f" Preguntas: {top_n}")
            self._log(f"=============================================\n")

            self._ensure_phoenix_running()

            # 2. Ejecutar a través de los scripts sh/ (.sh o .ps1) según OS
            if sys.platform == "win32":
                script_path = self.project_dir / "sh" / "lanzar_beta.ps1"
                cmd = [
                    "powershell",
                    "-ExecutionPolicy", "Bypass",
                    "-File", str(script_path),
                    "-InputFile", input_filename,
                    "-Perfil", profile,
                    "-Modelo", model,
                    "-TopN", str(top_n)
                ]
            else:
                script_path = self.project_dir / "sh" / "lanzar_beta.sh"
                cmd = [
                    "bash",
                    str(script_path),
                    input_filename,
                    profile,
                    model,
                    str(top_n)
                ]

            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"

            process = subprocess.Popen(
                cmd,
                cwd=str(self.project_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
                bufsize=1
            )

            for line in iter(process.stdout.readline, ''):
                if line:
                    self._log(line.rstrip())

            process.stdout.close()
            process.wait()

            if process.returncode == 0:
                self._set_status("Estado: ¡Completado!", "#10B981")
                self._log("\n✅ [ÉXITO] ¡Proceso terminado con éxito!")
            else:
                self._set_status("Estado: Error", "#EF4444")
                self._log(f"\n❌ [ERROR] El proceso terminó con código de error {process.returncode}")

        except Exception as e:
            self._log(f"\n❌ [EXCEPCIÓN] {str(e)}")
            self._set_status("Estado: Error", "#EF4444")

        finally:
            self._set_btn("normal", "🚀 GENERAR CUESTIONARIO")

if __name__ == "__main__":
    app = QnAGuiApp()
    app.mainloop()
