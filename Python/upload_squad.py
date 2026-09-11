import json
import pandas as pd
from pathlib import Path

def main():
    print("Conectando al servidor local de Phoenix (http://127.0.0.1:6006)...")
    try:
        import os
        os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = "http://127.0.0.1:6006"
        from phoenix.client import Client
        client = Client()
    except Exception as e:
        print(f"Error al conectar con Phoenix: {e}")
        return

    squad_path = Path("../train-v2.0.json")
    if not squad_path.exists():
        squad_path = Path("train-v2.0.json")

    print(f"Cargando dataset SQuAD desde: {squad_path.resolve()}")
    try:
        with open(squad_path, 'r', encoding='utf-8') as f:
            squad_data = json.load(f)
    except FileNotFoundError:
        print(f"No se encontró el archivo {squad_path}.")
        return

    # Preparar el directorio de salida para los contextos (los archivos .txt para tu GUI)
    txt_output_dir = Path("inputs/squad_samples")
    txt_output_dir.mkdir(parents=True, exist_ok=True)

    records = []
    posibles = 0
    imposibles = 0
    contextos_guardados = set()
    
    file_counter = 1

    for article in squad_data.get('data', []):
        for paragraph in article.get('paragraphs', []):
            context = paragraph.get('context', '')
            
            # Queremos guardar el contexto como un archivo .txt independiente para probar la GUI
            if context not in contextos_guardados and len(contextos_guardados) < 10:
                txt_filename = txt_output_dir / f"squad_contexto_{file_counter}.txt"
                with open(txt_filename, "w", encoding="utf-8") as txt_file:
                    txt_file.write(context)
                contextos_guardados.add(context)
                file_counter += 1

            for qa in paragraph.get('qas', []):
                question = qa.get('question', '')
                is_impossible = qa.get('is_impossible', False)
                
                # Equilibrar el dataset: máximo 75 posibles y 75 imposibles
                if is_impossible and imposibles >= 75:
                    continue
                if not is_impossible and posibles >= 75:
                    continue

                if not is_impossible and qa.get('answers'):
                    answer = qa['answers'][0].get('text', '')
                    posibles += 1
                else:
                    answer = "IMPOSSIBLE_TO_ANSWER"
                    imposibles += 1
                
                records.append({
                    "context": context,
                    "question": question,
                    "reference_answer": answer,
                    "is_impossible": str(is_impossible)
                })
                
                if posibles >= 75 and imposibles >= 75:
                    break
            if posibles >= 75 and imposibles >= 75:
                break
        if posibles >= 75 and imposibles >= 75:
            break

    df = pd.DataFrame(records)
    print(f"Muestra extraída: {posibles} Posibles | {imposibles} Imposibles (Total {len(df)})")
    print(f"Se crearon {len(contextos_guardados)} archivos .txt de contexto en: {txt_output_dir}")

    print("Subiendo Dataset Balanceado a Arize Phoenix...")
    try:
        # Si ya existe con el mismo nombre, Phoenix creará una nueva versión
        dataset = client.datasets.create_dataset(
            name="SQuAD_v2_Balanced",
            dataframe=df,
            input_keys=["context", "question"],
            output_keys=["reference_answer", "is_impossible"],
            dataset_description="Dataset SQuAD 2.0 Balanceado (50% posibles, 50% imposibles) para evaluar alucinaciones."
        )
        print("¡Dataset subido exitosamente a Phoenix!")
    except Exception as e:
        print(f"Error al subir el dataset a Phoenix: {e}")

if __name__ == "__main__":
    main()
