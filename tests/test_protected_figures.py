"""Regression checks for removal and corruption, without touching frozen assets."""
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
import hashlib
import importlib.util
import io
import json
import tempfile
import unittest

SPEC=importlib.util.spec_from_file_location('guard',Path(__file__).parents[1]/'scripts/verify_protected_figures.py')
guard=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(guard)

class ProtectedFigures(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        def put(name,content):
            p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)
        self.put=put
        put('main.tex',r'\input{sections/problem}')
        self.source='\n'.join(
            r'\begin{figure}\includegraphics{'+asset+r'}\label{'+label+r'}\end{figure}'
            for label,asset in guard.REQUIRED.items())
        put('sections/problem.tex',self.source)
        for asset in guard.REQUIRED.values():put(asset,'fixture image')
        put('figures/ieee39_single_line.tex','editable fixture')
        put('figures/frozen/original.tex','frozen fixture')
        frozen=self.root/'figures/frozen/original.tex'
        put('figures/frozen/PROTECTED_FIGURES.json',json.dumps({'files':{
            'figures/frozen/original.tex':hashlib.sha256(frozen.read_bytes()).hexdigest()}}))
        for field,value in [('ROOT',self.root),('MANIFEST',self.root/'figures/frozen/PROTECTED_FIGURES.json')]:
            patcher=patch.object(guard,field,value);patcher.start();self.addCleanup(patcher.stop)

    def verify(self):
        with redirect_stdout(io.StringIO()):return guard.verify()

    def test_intact_assets_and_inclusions_pass(self):
        self.assertTrue(self.verify()['both_figures_in_active_article_source'])

    def test_frozen_source_corruption_is_rejected(self):
        self.put('figures/frozen/original.tex','changed')
        with self.assertRaisesRegex(RuntimeError,'Protected file changed'):self.verify()

    def test_existing_image_but_removed_float_is_rejected(self):
        self.put('sections/problem.tex',self.source.splitlines()[0])
        with self.assertRaisesRegex(RuntimeError,'removed or duplicated'):self.verify()

    def test_commented_out_image_is_rejected(self):
        self.put('sections/problem.tex','\n'.join('% '+s for s in self.source.splitlines()))
        with self.assertRaisesRegex(RuntimeError,'removed or duplicated'):self.verify()

    def test_removed_section_is_rejected(self):
        self.put('main.tex','Article without the problem section')
        with self.assertRaisesRegex(RuntimeError,'removed or duplicated'):self.verify()

    def test_wrong_image_with_same_caption_is_rejected(self):
        self.put('sections/problem.tex',self.source.replace('narrative_topology.pdf','unrelated.pdf'))
        with self.assertRaisesRegex(RuntimeError,'no longer visibly included'):self.verify()

if __name__=='__main__':unittest.main()
