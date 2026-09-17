#!/usr/bin/env python3
"""
Módulo para descarga, procesamiento y exportación del Dataset SQuAD 2.0.
Procesa 'train-v2.0.json', añana contexts/questions/answers y exporta a 'resultadoBase.csv'.
"""

import os
import sys
import json
import urllib.request
from pathlib import Path
import pandas as pd

def procesar_squad_dataset(
    input_json_name: str = "train-v2.0.json",
    output_csv_name: str = "resultadoBase.csv"
) -> pd.DataFrame:
    """
    Descarga train-v2.0.json si no existe, procesa el JSON aplanando el dataset
    y genera resultadoBase.csv y resultadoPorContexto.csv.
    """
    project_dir = Path(__file__).resolve().parent.parent
    inputs_dir = project_dir / "inputs"
    outputs_dir = project_dir / "outputs" / "processed"
    
    inputs_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    
    # Buscar el JSON en inputs/ o en la raíz
    json_path = inputs_dir / input_json_name
    if not json_path.exists():
        root_json = project_dir / input_json_name
        if root_json.exists():
            json_path = root_json
        else:
            url = "https://rajpurkar.github.io/SQuAD-explorer/dataset/train-v2.0.json"
            print(f"[DatasetLoader] Descargando dataset SQuAD 2.0 desde {url}...", flush=True)
            urllib.request.urlretrieve(url, str(json_path))
            print(f"[DatasetLoader] Descarga completada en: {json_path}", flush=True)

    print(f"[DatasetLoader] Leyendo y aplanando {json_path.name}...", flush=True)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []
    for article in data.get("data", []):
        title = article.get("title", "")
        for paragraph in article.get("paragraphs", []):
            context = paragraph.get("context", "")
            for qa in paragraph.get("qas", []):
                rows.append({
                    "title": title,
                    "context": context,
                    "question": qa.get("question", ""),
                    "id": qa.get("id", ""),
                    "is_impossible": qa.get("is_impossible", False),
                    "answers": qa.get("answers", []),
                })

    df = pd.DataFrame(rows)
    print(f"[DatasetLoader] Total de preguntas procesadas: {len(df)}", flush=True)

    # Agrupar por contexto
    df_por_contexto = (
        df.groupby("context")["question"]
        .apply(list)
        .reset_index(name="questions")
    )
    df_por_contexto["num_questions"] = df_por_contexto["questions"].apply(len)
    df_por_contexto["question_lens"] = df_por_contexto["questions"].apply(
        lambda qs: [len(q.split()) for q in qs]
    )
    df_por_contexto["avg_question_len"] = df_por_contexto["question_lens"].apply(
        lambda lens: sum(lens) / len(lens) if len(lens) > 0 else 0
    )

    # Exportar CSVs
    root_csv = project_dir / output_csv_name
    df.to_csv(root_csv, index=False)
    df.to_csv(outputs_dir / output_csv_name, index=False)
    df_por_contexto.to_csv(outputs_dir / "resultadoPorContexto.csv", index=False)

    print(f"[DatasetLoader] ✅ Exportado exitosamente a:")
    print(f" - {root_csv}")
    print(f" - {outputs_dir / output_csv_name}")
    print(f" - {outputs_dir / 'resultadoPorContexto.csv'}", flush=True)

    return df

if __name__ == "__main__":
    procesar_squad_dataset()
