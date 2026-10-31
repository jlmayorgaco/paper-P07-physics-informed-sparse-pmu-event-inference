"""Compile and visually-audit the editable phased method diagram."""
from pathlib import Path
import json, shutil, subprocess
import pymupdf
ROOT=Path(__file__).resolve().parents[1]

def build():
    out=ROOT/'build/method_architecture';out.mkdir(parents=True,exist_ok=True)
    run=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',
        f'-output-directory={out}','main.tex'],cwd=ROOT/'figures/method_architecture',
        capture_output=True,text=True)
    (out/'compile_stdout.txt').write_text(run.stdout+run.stderr)
    if run.returncode:raise RuntimeError(run.stdout[-4000:])
    pdf=pymupdf.open(out/'main.pdf');assert len(pdf)==1
    page=pdf[0];assert not page.get_images()
    drawings=page.get_drawings()
    # The 19 processing blocks have fixed widths, unlike phase frames and footer.
    boxes=[d['rect'] for d in drawings if d['fill'] is not None
           and 100<d['rect'].width<150 and 30<d['rect'].height<80]
    assert len(boxes)==19,('processing block count',len(boxes))
    for i,a in enumerate(boxes):
        for b in boxes[i+1:]:assert not a.intersects(b),'Overlapping processing blocks'
    wires=[d for d in drawings if d['fill'] is None and abs(d['width']-.6476)<.015]
    words=page.get_text('words');segments=0
    for d in wires:
        for item in d['items']:
            if item[0]!='l':continue
            a,b=item[1:];assert abs(a.x-b.x)<.05 or abs(a.y-b.y)<.05,'Nonorthogonal connector'
            box=pymupdf.Rect(min(a.x,b.x)-.25,min(a.y,b.y)-.25,
                             max(a.x,b.x)+.25,max(a.y,b.y)+.25)
            for w in words:
                assert not box.intersects(pymupdf.Rect(w[:4])),('Connector over text',w[4])
            # Wires may terminate on block borders, never pass through a block.
            for node in boxes:
                interior=node+(1,1,-1,-1)
                assert not box.intersects(interior),'Connector enters a processing block'
            segments+=1
    audit=dict(processing_blocks=19,phases=4,orthogonal_connector_segments=segments,
               block_overlaps=0,connector_text_overlaps=0,connectors_through_blocks=0,
               raster_images=0,pdf_size_pt=[page.rect.width,page.rect.height],
               scope='Implemented R11 mechanism in sections/article_method.tex')
    target=ROOT/'figures/generated/narrative_architecture.pdf'
    shutil.copy2(out/'main.pdf',target)
    page.get_pixmap(matrix=pymupdf.Matrix(2.2,2.2)).save(target.with_suffix('.png'))
    (ROOT/'generated/method_architecture_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audit,indent=2))

if __name__=='__main__':build()
