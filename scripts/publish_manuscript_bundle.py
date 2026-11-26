"""Publish separately compiled documents and a combined copy for review."""
from pathlib import Path
import hashlib
import json
import os
import shutil

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'output/pdf'


def publish_copy(source, name):
    destination = OUTPUT / name
    temporary = destination.with_suffix('.tmp.pdf')
    shutil.copyfile(source, temporary)
    os.replace(temporary, destination)
    return destination


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (ROOT / 'build').mkdir(exist_ok=True)
    with pymupdf.open(ROOT / 'main.pdf') as article, pymupdf.open(ROOT / 'supplement.pdf') as supplement:
        assert len(article) > 0 and len(supplement) > 0
        assert not any('APPENDIX A.' in p.get_text() for p in article)
        assert 'Supplementary Material' in supplement[0].get_text()
        merged = pymupdf.open()
        merged.insert_pdf(article)
        merged.insert_pdf(supplement)
        toc = [[1, 'Main article', 1]]
        toc += [[level + 1, title, page] for level, title, page in article.get_toc()]
        toc += [[1, 'Supplementary material', len(article) + 1]]
        toc += [[level + 1, title, page + len(article)] for level, title, page in supplement.get_toc()]
        merged.set_toc(toc)
        merged.set_metadata({'title': 'P07 - Article and supplementary material',
                             'subject': 'Combined review copy; two independently compiled documents'})
        review = OUTPUT / 'P07_Event_Attribution_Review_Bundle.pdf'
        temporary = review.with_suffix('.tmp.pdf')
        merged.save(temporary, garbage=4, deflate=True)
        merged.close()
        os.replace(temporary, review)
        with pymupdf.open(review) as check:
            assert len(check) == len(article) + len(supplement)
            for offset, source in [(0, article), (len(article), supplement)]:
                for i, page in enumerate(source):
                    assert check[offset + i].get_text() == page.get_text(), (offset, i)
        page_counts = {'article': len(article), 'supplement': len(supplement),
                       'review_bundle': len(article) + len(supplement)}

    with pymupdf.open(ROOT / 'historical_notes.pdf') as historical:
        assert len(historical) > 0
        assert 'Historical Technical Notes' in historical[0].get_text()
        page_counts['historical_notes'] = len(historical)

    artifacts = [
        publish_copy(ROOT / 'main.pdf', 'P07_Event_Attribution_Article.pdf'),
        publish_copy(ROOT / 'supplement.pdf', 'P07_Event_Attribution_Supplement.pdf'),
        publish_copy(ROOT / 'historical_notes.pdf', 'P07_Historical_Technical_Notes.pdf'),
        # Keep existing delivery names current for collaborators' saved links.
        publish_copy(ROOT / 'main.pdf', 'P07_Physics_Informed_State_Reconstruction_Event_Source_Inference.pdf'),
        publish_copy(ROOT / 'supplement.pdf', 'P07_Physics_Informed_State_Reconstruction_Event_Source_Inference_Supplement.pdf'),
        review,
    ]
    manifest = {'pages': page_counts, 'combined_text_matches_individual_documents': True,
                'artifacts': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in artifacts}}
    (ROOT / 'build/manuscript_bundle_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
