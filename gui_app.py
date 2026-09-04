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

        self.project_dir = Path(__file__).resolve().parent
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
        self.profile_combo = ctk.CTkComboBox(
            left_col, 
            values=["estudiante universitario", "técnico avanzado", "principiante", "estudiante secundario"]
        )
        self.profile_combo.set("estudiante universitario")
        self.profile_combo.pack(fill="x", padx=15, pady=(0, 8))

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
        self.questions_combo = ctk.CTkComboBox(
            left_col, 
            values=["5", "3", "8", "10"]
        )
        self.questions_combo.set("5")
        self.questions_combo.pack(fill="x", padx=15, pady=(0, 15))

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
        self.log_textbox.insert("end", text + "\n")
        self.log_textbox.see("end")

    def _open_outputs_folder(self):
        folder = str(self.outputs_dir)
        if sys.platform == "win32":
            os.startfile(folder)
        elif sys.platform == "darwin":
            subprocess.run(["open", folder])
        else:
            subprocess.run(["xdg-open", folder])

    def _start_generation_thread(self):
        if not self.selected_file_path:
            messagebox.showwarning("Atención", "Por favor selecciona un archivo primero.")
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
            profile = self.profile_combo.get()
            model = self.model_combo.get()
            top_n = self.questions_combo.get()

            self._log(f"\n=============================================")
            self._log(f" Ejecutando Sistema QnA RAG Multi-Agente")
            self._log(f" Archivo : {input_filename}")
            self._log(f" Perfil  : {profile}")
            self._log(f" Modelo  : {model}")
            self._log(f" Preguntas: {top_n}")
            self._log(f"=============================================\n")

            # 2. Ejecutar Python/main.py
            cmd = [
                sys.executable,
                str(self.project_dir / "Python" / "main.py"),
                "--input", input_filename,
                "--perfil", profile,
                "--modelo", model,
                "--top_n", str(top_n)
            ]

            env = os.environ.copy()
            env["PYTHONPATH"] = str(self.project_dir / "python") + ":" + str(self.project_dir / "Python")

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
                    self._log(line.strip())

            process.stdout.close()
            process.wait()

            if process.returncode == 0:
                self.status_label.configure(text="Estado: ¡Completado!", text_color="#10B981")
                self._log("\n✅ [ÉXITO] ¡Proceso terminado con éxito!")
            else:
                self.status_label.configure(text="Estado: Error", text_color="#EF4444")
                self._log(f"\n❌ [ERROR] El proceso terminó con código de error {process.returncode}")

        except Exception as e:
            self._log(f"\n❌ [EXCEPCIÓN] {str(e)}")
            self.status_label.configure(text="Estado: Error", text_color="#EF4444")

        finally:
            self.run_btn.configure(state="normal", text="🚀 GENERAR CUESTIONARIO")

if __name__ == "__main__":
    app = QnAGuiApp()
    app.mainloop()
