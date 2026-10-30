"""Real PyTorch checkpoint tests; no avatar weights, GPU, or downloads needed."""
import ast
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import torch
from diffusers import UNet2DConditionModel
import importlib.util

# Load the exact production helper without importing the optional Diffusers stack.
SOURCE = Path(__file__).resolve().parents[1] / 'upstream/musetalk/models/unet.py'
tree = ast.parse(SOURCE.read_text())
function = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                and n.name == 'load_inference_weights')
namespace = {'torch': torch, 'zipfile': zipfile}
exec(compile(ast.Module(body=[function], type_ignores=[]), str(SOURCE), 'exec'), namespace)
load = namespace['load_inference_weights']


class TinyInference(torch.nn.Module):
    def __init__(self, width=4):
        super().__init__()
        self.layer = torch.nn.Linear(width, width)
        self.register_buffer('scale', torch.ones(width))

    def forward(self, x):
        return self.layer(x) * self.scale


class WeightLoadingTests(unittest.TestCase):
    def test_real_diffusers_unet_preserves_predictions(self):
        spec = importlib.util.spec_from_file_location('aria_unet', SOURCE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        config = dict(sample_size=8, in_channels=8, out_channels=4,
                      down_block_types=('CrossAttnDownBlock2D',),
                      up_block_types=('CrossAttnUpBlock2D',),
                      block_out_channels=(32,), layers_per_block=1,
                      cross_attention_dim=384, attention_head_dim=8)
        torch.manual_seed(7)
        original = UNet2DConditionModel(**config).eval()
        latent = torch.randn(1, 8, 8, 8)
        audio = torch.randn(1, 4, 384)
        with torch.no_grad():
            expected = original(latent, 0, encoder_hidden_states=audio).sample
        with tempfile.TemporaryDirectory() as tmp:
            import json
            path = Path(tmp) / 'weights.pth'
            cfg = Path(tmp) / 'config.json'
            cfg.write_text(json.dumps(config))
            torch.save(original.state_dict(), path)
            restored = module.UNet(cfg, path, device=torch.device('cpu'))
            with torch.no_grad():
                actual = restored.model(latent, 0, encoder_hidden_states=audio).sample
            torch.testing.assert_close(actual, expected, rtol=0, atol=0)

    def test_saved_weights_preserve_output_and_use_meta_initialization(self):
        original = TinyInference().eval()
        x = torch.arange(8, dtype=torch.float32).reshape(2, 4)
        expected = original(x).detach()
        for use_zip in (True, False):
            with self.subTest(zip=use_zip), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'weights.pth'
                torch.save(original.state_dict(), path, _use_new_zipfile_serialization=use_zip)
                def factory(**config):
                    model = TinyInference(**config)
                    self.assertTrue(all(p.is_meta for p in model.parameters()))
                    return model
                with patch.object(torch, 'load', wraps=torch.load) as observed:
                    restored = load(factory, {'width': 4}, path)
                self.assertEqual(observed.call_args.kwargs['mmap'], use_zip)
                self.assertTrue(observed.call_args.kwargs['weights_only'])
                torch.testing.assert_close(restored(x), expected, rtol=0, atol=0)
                self.assertFalse(restored.training)
                self.assertTrue(all(not p.requires_grad for p in restored.parameters()))

    def test_missing_or_wrong_shape_weights_fail(self):
        original = TinyInference()
        for state in ({}, {'layer.weight': torch.ones(2, 2),
                          'layer.bias': torch.ones(4), 'scale': torch.ones(4)}):
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'bad.pth'
                torch.save(state, path)
                with self.assertRaises(RuntimeError):
                    load(TinyInference, {}, path)


if __name__ == '__main__':
    unittest.main()
