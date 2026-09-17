#!/usr/bin/env python3
"""
Módulo de Limpieza, Procesamiento y Exportación del Dataset SQuAD 2.0.
Aplica limpieza de texto UTF-8, remoción de espacios/control de caracteres,
extracción de respuestas principales, métricas de longitud, deduplicación
y exportación automatizada a CSVs y archivos de muestra para RAG.
"""

import os
import sys
import json
import re
import urllib.request
from pathlib import Path
import pandas as pd

def limpiar_texto(texto: str) -> str:
    """
    Normaliza caracteres no imprimibles, colapsa espacios en blanco repetidos
    y preserva tildes y caracteres UTF-8 sin corrupción.
    """
    if not isinstance(texto, str):
        return ""
    # Normalizar saltos de línea y tabulaciones espurias
    t = re.sub(r'[\r\t\xa0\u200b]+', ' ', texto)
    # Colapsar múltiples espacios a uno solo
    t = re.sub(r'[ ]+', ' ', t)
    # Colapsar saltos de línea repetidos
    t = re.sub(r'\n{3,}', '\n\n', t)
    return t.strip()

def procesar_squad_dataset(
    input_json_name: str = "train-v2.0.json",
    output_csv_name: str = "resultadoBase.csv",
    num_samples_to_export: int = 10
) -> pd.DataFrame:
    """
    Descarga train-v2.0.json si no existe, limpia los registros,
    elimina duplicados, extrae métricas y exporta los CSVs limpios.
    """
    project_dir = Path(__file__).resolve().parent.parent
    inputs_dir = project_dir / "inputs"
    outputs_dir = project_dir / "outputs" / "processed"
    samples_dir = inputs_dir / "squad_samples"
    
    inputs_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    samples_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Localizar o descargar dataset
    json_path = inputs_dir / input_json_name
    if not json_path.exists():
        root_json = project_dir / input_json_name
        if root_json.exists():
            json_path = root_json
        else:
            url = "https://rajpurkar.github.io/SQuAD-explorer/dataset/train-v2.0.json"
            print(f"[DatasetLoader] Descargando SQuAD 2.0 desde {url}...", flush=True)
            urllib.request.urlretrieve(url, str(json_path))
            print(f"[DatasetLoader] Descarga completada en: {json_path}", flush=True)

    print(f"[DatasetLoader] Leyendo y aplanando {json_path.name}...", flush=True)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 2. Aplanar y aplicar limpieza inicial de caracteres
    raw_rows = []
    for article in data.get("data", []):
        title = limpiar_texto(article.get("title", ""))
        for paragraph in article.get("paragraphs", []):
            context = limpiar_texto(paragraph.get("context", ""))
            for qa in paragraph.get("qas", []):
                question = limpiar_texto(qa.get("question", ""))
                qa_id = qa.get("id", "").strip()
                is_impossible = qa.get("is_impossible", False)
                answers = qa.get("answers", [])
                
                # Extraer respuesta principal limpia si está disponible
                primary_answer = ""
                if answers and isinstance(answers, list) and len(answers) > 0:
                    primary_answer = limpiar_texto(answers[0].get("text", ""))
                    
                raw_rows.append({
                    "title": title,
                    "context": context,
                    "question": question,
                    "id": qa_id,
                    "is_impossible": is_impossible,
                    "primary_answer": primary_answer,
                    "has_answer": not is_impossible and len(primary_answer) > 0
                })

    df_raw = pd.DataFrame(raw_rows)
    total_raw = len(df_raw)

    # 3. Filtrar registros inválidos o vacíos
    df_clean = df_raw[(df_raw["context"].str.len() > 20) & (df_raw["question"].str.len() > 5)].copy()

    # 4. Eliminar duplicados exactos (contexto, pregunta)
    df_clean = df_clean.drop_duplicates(subset=["context", "question"]).copy()
    total_clean = len(df_clean)

    # 5. Calcular métricas de longitud
    df_clean["context_words"] = df_clean["context"].apply(lambda c: len(c.split()))
    df_clean["question_words"] = df_clean["question"].apply(lambda q: len(q.split()))
    df_clean["answer_words"] = df_clean["primary_answer"].apply(lambda a: len(a.split()) if a else 0)

    # 6. Agrupar por contexto para análisis
    df_por_contexto = (
        df_clean.groupby("context")["question"]
        .apply(list)
        .reset_index(name="questions")
    )
    df_por_contexto["num_questions"] = df_por_contexto["questions"].apply(len)
    df_por_contexto["context_words"] = df_por_contexto["context"].apply(lambda c: len(c.split()))
    df_por_contexto["question_lens"] = df_por_contexto["questions"].apply(
        lambda qs: [len(q.split()) for q in qs]
    )
    df_por_contexto["avg_question_len"] = df_por_contexto["question_lens"].apply(
        lambda lens: sum(lens) / len(lens) if len(lens) > 0 else 0
    )

    # 7. Exportar CSVs
    root_csv = project_dir / output_csv_name
    df_clean.to_csv(root_csv, index=False, encoding="utf-8")
    df_clean.to_csv(outputs_dir / output_csv_name, index=False, encoding="utf-8")
    df_por_contexto.to_csv(outputs_dir / "resultadoPorContexto.csv", index=False, encoding="utf-8")

    # 8. Exportar muestras individuales para probar en la GUI RAG
    if num_samples_to_export > 0:
        unique_contexts = df_clean["context"].unique()[:num_samples_to_export]
        for idx, sample_ctx in enumerate(unique_contexts, start=1):
            sample_file = samples_dir / f"squad_contexto_{idx}.txt"
            sample_file.write_text(sample_ctx, encoding="utf-8")

    # Reporte de Limpieza
    print("\n=============================================", flush=True)
    print("      REPORTE DE LIMPIEZA DE DATASET", flush=True)
    print("=============================================", flush=True)
    print(f" Total filas originales   : {total_raw}", flush=True)
    print(f" Filas eliminadas (dups)  : {total_raw - total_clean}", flush=True)
    print(f" Total filas limpias      : {total_clean}", flush=True)
    print(f" Contextos únicos limpios : {len(df_por_contexto)}", flush=True)
    print(f" Prom. palabras/contexto  : {df_clean['context_words'].mean():.1f}", flush=True)
    print(f" Prom. palabras/pregunta  : {df_clean['question_words'].mean():.1f}", flush=True)
    print("=============================================", flush=True)
    print(f" ✅ CSV base exportado en: {root_csv}", flush=True)
    print(f" ✅ CSV por contexto en : {outputs_dir / 'resultadoPorContexto.csv'}", flush=True)
    print(f" ✅ {num_samples_to_export} contextos de muestra exportados en: {samples_dir}\n", flush=True)

    return df_clean

if __name__ == "__main__":
    procesar_squad_dataset()
