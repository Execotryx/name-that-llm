"""Readiness regressions; target/encoder doubles establish software behavior only."""
from __future__ import annotations

import copy
import runpy
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
from typing import Any, cast

import numpy as np
import pandas as pd

from ntl.capacity import SCALES, workload, profile_capacity, verify_capacity
from ntl.common import digest, identity, read_json, write_json
from ntl.environment import runtime_profile
from ntl.gates import require_gate
from ntl.labels import CLASSES
from ntl.provenance import execution
from ntl.resources import resource_reasons, target_reasons
from ntl.runner import eligibility
from ntl.runtime import gpu_memory
from ntl.schema import DEFAULT_CONTRACT
from ntl.smoke import cpu_smoke, neural_smoke, _evidence
from ntl.release import replay
from test_contracts import fixture, dev_root
from target_fixture import target_record


class EncoderDouble:
    manifest = {"revision": "a" * 40}
    device = "cpu"
    batch_size = 8

    def __init__(self):
        self.calls = []
        self.cache_calls = 0

    def runtime(self):
        return {**runtime_profile(), "kind": "neural", "settings": {"device": "cpu", "batch_size": self.batch_size}}

    def preflight(self):
        return self.runtime()

    def load(self):
        pass

    def encode(self, texts):
        self.calls.append(len(texts))
        return np.zeros((len(texts), 2), dtype=np.float32)

    def cache(self, frame, directory, **kwargs):
        self.cache_calls += 1
        return self.encode(frame.text)

    def token_profile(self, texts):
        lengths = [len(t.split()) + 2 for t in texts]
        n = sum(v > 512 for v in lengths)
        return {"rows": len(lengths), "min": min(lengths), "max": max(lengths),
                "truncated_rows": n, "truncation_rate": n / len(texts), "max_length": 512}


class CountingModel:
    def __init__(self, encoder=None):
        self.encoder = encoder
        self.calls = []
        self.config = {"architecture": "F" if encoder is not None else "S", "C": 2}

    def predict_proba(self, texts):
        self.calls.append(list(texts))
        if self.encoder is not None:
            self.encoder.encode(texts)
        return np.full((len(texts), 18), 1 / 18)

    def predict(self, texts):
        return [CLASSES[i] for i in self.predict_proba(texts).argmax(axis=1)]


class Readiness(unittest.TestCase):
    def test_export_drift_and_normalization(self):
        functions = runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/verify_runtime.py"))
        normalize, check = functions["requirements"], functions["check_export"]
        self.assertEqual(normalize('# header\nPackaging==26.3\n\n'), {'packaging==26.3'})
        self.assertNotEqual(normalize('packaging==26.3'), normalize('packaging==26.4'))
        self.assertNotEqual(normalize('packaging==26.3'), normalize('packaging==26.3; python_version<"3"'))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            export = root / "requirements-runtime.txt"
            with patch('subprocess.check_output', return_value='packaging==26.3\npandas==3.1.0\n'):
                for bad in ('pandas==3.1.0\n', 'pandas==3.1.0\npackaging==26.4\n', 'packaging==26.3\n'):
                    export.write_text(bad)
                    with self.assertRaisesRegex(ValueError, 'Runtime export drift'):
                        check(root)
                export.write_text('# comment\npandas==3.1.0\npackaging==26.3\n')
                self.assertEqual(check(root)['status'], 'passed')

    def test_capacity_counts_diversity_cache_bypass_and_binding(self):
        frame = fixture(2)
        encoder = EncoderDouble()
        model = CountingModel(encoder)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            profile = profile_capacity(frame, model, root, DEFAULT_CONTRACT,
                                       allowed_ids=set(frame.id), manifest_hash='synthetic')
            self.assertEqual(sum(map(len, model.calls)), sum(SCALES) + 64)
            self.assertEqual(encoder.cache_calls, 0)
            self.assertGreater(len({t for call in model.calls for t in call}), 1)
            self.assertIn(64, encoder.calls)
            self.assertGreaterEqual(profile['stress']['tokens']['min'], 512)
            self.assertEqual(profile['workload'], workload(frame.iloc[::-1], set(frame.id), 'synthetic'))
            e = {'gate':'G1b', 'execution':execution(encoder), 'development_manifest_hash':'synthetic',
                 'capacity':profile, 'files':profile['files'], 'scale_seconds':profile['scale_seconds'],
                 'inference_seconds':profile['scale_seconds']['4000']}
            verify_capacity(e)
            for mutate in ('legacy','scale','time','batch','batch_identity','hash','files','tokens'):
                bad = copy.deepcopy(e)
                if mutate == 'legacy': bad.pop('capacity')
                if mutate == 'scale': bad['capacity']['scale_rows'].pop('8000')
                if mutate == 'time': bad['inference_seconds'] *= 2
                if mutate == 'batch': bad['capacity']['stress']['rows'] = 7
                if mutate == 'batch_identity': bad['execution']['runtime']['settings']['batch_size'] = 16
                if mutate == 'hash': bad['capacity']['workload_hash'] = 'wrong'
                if mutate == 'files': bad['files'] = {}
                if mutate == 'tokens': bad['capacity']['stress']['tokens']['min'] = 10
                with self.subTest(mutate=mutate), self.assertRaises(ValueError): verify_capacity(bad)
            with self.assertRaisesRegex(ValueError, 'allowlisted'):
                profile_capacity(frame, model, root, DEFAULT_CONTRACT, allowed_ids={'wrong'}, manifest_hash='synthetic')
            with self.assertRaisesRegex(ValueError, 'Preserve prior'):
                profile_capacity(frame, model, root, DEFAULT_CONTRACT, allowed_ids=set(frame.id), manifest_hash='synthetic')
        # Incorrect predictions never yield an accepted capacity record.
        with tempfile.TemporaryDirectory() as tmp, patch.object(model, 'predict', return_value=[]):
            with self.assertRaises(ValueError):
                profile_capacity(frame, model, Path(tmp), DEFAULT_CONTRACT, allowed_ids=set(frame.id), manifest_hash='synthetic')

    def test_resource_boundaries_and_bad_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); write_json(root/'manifest.json', {})
            valid = target_record(root, fixture(2))
            self.assertEqual(resource_reasons(valid), [])
            for field, value, message in [('wall_seconds',70,'time'),('peak_memory_bytes',80,'memory'),
                                           ('inference_seconds',70,'time')]:
                e = copy.deepcopy(valid); e[field] = value
                self.assertTrue(any(message in r for r in resource_reasons(e)))
            e = copy.deepcopy(valid); e['wall_seconds'] = 69.999; e['peak_memory_bytes'] = 79.999
            self.assertEqual(resource_reasons(e), [])
            for field in ('available_memory_bytes','limit_seconds','wall_seconds','inference_seconds','peak_memory_bytes'):
                for value in (float('nan'),float('inf'),-1,None,True):
                    e = copy.deepcopy(valid); e[field] = value
                    with self.subTest(field=field,value=value), self.assertRaises(ValueError): resource_reasons(e)
            for field in ('available_memory_bytes','limit_seconds','inference_seconds'):
                e = copy.deepcopy(valid); e[field] = 0
                with self.assertRaises(ValueError): resource_reasons(e)
            e = copy.deepcopy(valid); e.pop('resource_version')
            with self.assertRaisesRegex(ValueError,'revalidation'): resource_reasons(e)
            e = copy.deepcopy(valid); e['cold_restart'] = False
            self.assertTrue(target_reasons(e))

    def test_explicit_gpu_accounting_and_reserved_peak(self):
        properties = SimpleNamespace(name='synthetic device', total_memory=1000)
        cuda = SimpleNamespace(synchronize=Mock(), reset_peak_memory_stats=Mock(),
            get_device_properties=Mock(return_value=properties),max_memory_allocated=Mock(return_value=100),
            max_memory_reserved=Mock(return_value=200))
        with patch('importlib.import_module', return_value=SimpleNamespace(cuda=cuda)):
            gpu = gpu_memory('cuda:1',reset=True)
        assert gpu is not None
        for method in vars(cuda).values():
            self.assertTrue(all(c.args == ('cuda:1',) for c in method.call_args_list))
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); write_json(root/'manifest.json',{})
            e=target_record(root,fixture(2)); e['gpu']=gpu
            e['execution']['runtime']['settings']={'device':'cuda:1'}
            self.assertEqual(resource_reasons(e),[])
            e['gpu']['reserved_bytes']=800
            self.assertIn('Insufficient GPU memory reserve',resource_reasons(e))
            e['gpu']['device']='cuda:0'
            with self.assertRaisesRegex(ValueError,'encoder-device'): resource_reasons(e)

    def test_smoke_producer_consumer_and_workload_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'dev'; frame=fixture(10); dev_root(root,frame)
            protocol = read_json(root/'protocol.json'); protocol['encoder']['revision']='a'*40
            write_json(root/'protocol.json',protocol)
            manifest=read_json(root/'manifest.json'); manifest['files']['protocol.json']=digest(root/'protocol.json')
            write_json(root/'manifest.json',manifest)
            (root/'G1a.json').unlink()
            test=Path(tmp)/'test.csv'; frame[['id','text']].iloc[:3].to_csv(test,index=False)
            with patch('ntl.smoke.source_revision',return_value='SYNTHETIC'), patch('ntl.smoke.is_kaggle',return_value=True), patch('ntl.smoke.fit_model',return_value=CountingModel()):
                cpu=cpu_smoke(root,test,root/'cpu',available_memory=10**12,cold_restart=True)
            self.assertEqual(cpu['status'],'passed')
            require_gate(root/'G1a.json','G1a',digest(root/'manifest.json'))
            encoder=EncoderDouble()
            with patch('ntl.smoke.source_revision',return_value='SYNTHETIC'), patch('ntl.smoke.is_kaggle',return_value=True), patch('ntl.smoke.fit_model',return_value=CountingModel(encoder)):
                neural=neural_smoke(root,encoder,root/'neural',available_memory=10**12,limit_seconds=1000,cold_restart=True)
            self.assertEqual(neural['status'],'passed')
            neural_gate=root/'neural/G1b.json'
            require_gate(neural_gate,'G1b',digest(root/'manifest.json'),current=execution(encoder))
            _,costs=eligibility(root,neural_gate,encoder)
            self.assertEqual(costs['H'],costs['S']+costs['F'])
            # A slow extraction/probe stage must block even with fast measured inference.
            with patch('ntl.smoke.time.perf_counter',return_value=100), patch('ntl.smoke.is_kaggle',return_value=True), patch('ntl.smoke.peak_memory',return_value=1):
                blocked=_evidence(root,root/'neural',neural['capacity'],start=0,
                    available_memory=10**12,limit_seconds=100,cold_restart=True,revision='SYNTHETIC',phases={},encoder=encoder)
            self.assertEqual(blocked['status'],'blocked')
            self.assertIn('Insufficient time reserve',blocked['reasons'])
            # A falsely claimed passed record is still rejected by the same consumer rule.
            blocked['status']='passed'; write_json(root/'neural/blocked.json',blocked)
            with self.assertRaisesRegex(ValueError,'time reserve'):
                require_gate(root/'neural/blocked.json','G1b',digest(root/'manifest.json'),current=execution(encoder))
            neural['capacity']['workload']['sources'][0]['text_sha256']='0'*64
            neural['capacity']['workload_hash']=identity(neural['capacity']['workload'])
            write_json(neural_gate,neural)
            with self.assertRaisesRegex(ValueError,'workloads differ'): eligibility(root,neural_gate,encoder)
            # A bad neural attempt cannot damage the valid S-only route.
            self.assertEqual(eligibility(root,None,None)[0]['eligible'],['S'])
            self.assertFalse((root/'consumption_ledger.json').exists())
            with patch('ntl.smoke.source_revision',return_value='SYNTHETIC'), patch('ntl.smoke.profile_capacity',side_effect=MemoryError('synthetic OOM')), patch('ntl.smoke.fit_model',return_value=CountingModel(encoder)):
                with self.assertRaises(MemoryError):
                    neural_smoke(root,encoder,root/'failed-neural',available_memory=10**12,limit_seconds=1000)
            self.assertEqual(read_json(root/'failed-neural/G1b.json')['status'],'blocked')
            self.assertIn('synthetic OOM',(root/'failed-neural/incidents.jsonl').read_text())
            self.assertEqual(eligibility(root,None,None)[0]['eligible'],['S'])

    def test_encoder_token_summary_without_optional_execution(self):
        from ntl.encoder import FrozenEncoder
        from test_corrections import asset_tree
        with tempfile.TemporaryDirectory() as tmp:
            encoder=asset_tree(Path(tmp))
            encoder._tokenizer=lambda texts, **kwargs: {'input_ids':[[0]*len(t) for t in texts]}
            with patch.object(encoder,'load'):
                profile=FrozenEncoder.token_profile(encoder,['a'*10,'b'*600])
            self.assertEqual(profile['min'],10)
            self.assertEqual(profile['max'],600)
            self.assertEqual(profile['truncated_rows'],1)
            self.assertEqual(profile['truncation_rate'],.5)

    def test_bad_budgets_precede_expensive_work_and_reservation(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'out'
            for fn in (lambda: cpu_smoke(Path('none'),Path('none'),output,available_memory=0),
                       lambda: neural_smoke(Path('none'),None,output,available_memory=1,limit_seconds=float('inf')),
                       lambda: replay(Path('none'),Path('none'),output,available_memory=cast(Any,float('inf')))):
                with patch('ntl.smoke.source_revision') as revision, self.assertRaises(ValueError): fn()
                revision.assert_not_called()
                self.assertFalse(output.exists())
