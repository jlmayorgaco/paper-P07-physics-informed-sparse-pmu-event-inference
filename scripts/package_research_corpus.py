"""Package a portable reading corpus and its small numerical sources."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SGSMA = ROOT.parent / "SGSMA26-Physics-Informed-AD"
CORPUS = ROOT / "docs/corpus"
DEST = ROOT / "output/P07_Corpus_Conversaciones_2026-10-30.zip"


def main():
    manifest = json.loads((CORPUS / "MANIFEST.json").read_text())
    files = {}
    for name, meta in manifest["sources"].items():
        path = Path(name)
        path = path if path.is_absolute() else ROOT / path
        assert hashlib.sha256(path.read_bytes()).hexdigest() == meta["sha256"], path
        files[str(path.relative_to(ROOT.parent)).replace("\\", "/")] = path
    extra = list(CORPUS.iterdir()) + [
        ROOT / "generated/frozen/SOURCE_MANIFEST.csv",
        ROOT / "generated/frozen/continuous_20261029/MANIFEST.json",
        ROOT / "generated/frozen/shared_review_x01_20261030/MANIFEST.json",
        ROOT / "generated/frozen/ei_x02_20261030/MANIFEST.json",
        ROOT / "docs/ei-x02-results.md",
        ROOT / "docs/FINAL_REVIEW_X02.md",
        ROOT / "docs/PAPER_REVISION_X02.md",
        ROOT / "docs/WRITING_REVIEW_X02.md",
        ROOT / "output/pdf/P07_Event_Attribution_Article.pdf",
        ROOT / "sections/article_method.tex",
        ROOT / "sections/article_interpretation.tex",
        ROOT / "sections/article_information.tex",
        ROOT / "sections/article_ei_x02.tex",
        ROOT / "scripts/package_research_corpus.py",
        SGSMA / "experiments/PAPER_METHOD_DICE_X01/METHOD_AND_EXPERIMENTS.md",
        SGSMA / "experiments/PAPER_METHOD_DICE_X01/RESULTS.md",
    ]
    ei = ROOT / "generated/frozen/ei_x02_20261030"
    if ei.exists():
        extra += [p for p in ei.rglob('*') if p.is_file()]
    for path in extra:
        if path.is_file():
            files[str(path.relative_to(ROOT.parent)).replace("\\", "/")] = path
    prompt = """# Para continuar con otra conversación LLM

Lee primero paper-P07-physics-informed-sparse-pmu-event-inference/docs/corpus/README.md.
El autor quiere un método útil y publicable de detección, clasificación y
localización física con ocho PMU, más allá de un clasificador por etiquetas.

La decisión actual es cerrar el paper causal R11/nominal con C01 congelada,
no iniciar otra cadena de correcciones de buses. Este paquete conserva 32
ideas adjudicadas y __ROWS__ resultados con fuente/hash/denominador. También incluye
el artículo actual y el ensayo IEEE-39 X02 junto con la propuesta separada DICE/X01. Sus cifras externas
sintéticas NO son resultados IEEE-39 ni rendimiento local de R11.

No mezcles B2, E_B, E_J, R11 y DICE como etapas de un método ya validado.
No conviertas causalidad en tiempo real, masas en probabilidades calibradas,
ni desarrollo en confirmación. La imagen original de los eventos NO se cambia.
Conserva baselines y estados; no abras RAW0002, no recalibres ni hagas push.

Es un paquete de lectura y evidencia agregada, no una distribución completa
del simulador o del ejecutor científico. No contiene las trayectorias/matrices
originales ausentes de E_B ni resultados parciales de C01. El generador del
corpus usa los pequeños archivos incluidos; las simulaciones requieren los
repositorios y entornos completos originales.

Para ayudar al autor, distingue siempre: contribución implementada,
resultado ejecutado, evidencia negativa, propuesta y prueba que falta.
No inventes mejores métricas ni añadas todas las ideas al artículo principal.
"""
    prompt = prompt.replace('__ROWS__', str(manifest['result_rows']))
    DEST.parent.mkdir(exist_ok=True)
    inventory = {name: hashlib.sha256(path.read_bytes()).hexdigest()
                 for name, path in files.items()}
    with zipfile.ZipFile(DEST, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("START_HERE.md", prompt)
        for name, path in sorted(files.items()):
            archive.write(path, name)
        archive.writestr("PACKAGE_MANIFEST.json", json.dumps(inventory, indent=2))
    with zipfile.ZipFile(DEST) as archive:
        assert archive.testzip() is None
        for name, digest in inventory.items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == digest, name
    print(json.dumps({"path": str(DEST), "files": len(files) + 2,
                      "bytes": DEST.stat().st_size, "content_hashes_verified": True}, indent=2))


if __name__ == "__main__":
    main()
