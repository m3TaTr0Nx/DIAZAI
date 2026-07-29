from __future__ import annotations
import copy
from dataclasses import dataclass
import numpy as np
import torch
from torch import nn
from .algebra import NEIGHBORS, group_keys

torch.set_num_threads(1)
KEY_NAMES = tuple(group_keys().keys())
KEY_TENSORS = tuple(torch.tensor(v, dtype=torch.long) for v in group_keys().values())
NEIGHBOR_TENSOR = torch.tensor(NEIGHBORS, dtype=torch.long)


def group_mean(x: torch.Tensor, key: torch.Tensor) -> torch.Tensor:
    groups = int(key.max().item()) + 1
    sums = torch.zeros(groups, x.shape[1], dtype=x.dtype, device=x.device)
    sums.index_add_(0, key.to(x.device), x)
    counts = torch.bincount(key.to(x.device), minlength=groups).to(x.dtype).clamp_min(1).unsqueeze(1)
    return (sums / counts)[key.to(x.device)]


class MLPBaseline(nn.Module):
    def __init__(self, input_dim: int, classes: int, hidden: int = 24):
        super().__init__()
        self.network = nn.Sequential(nn.Linear(input_dim, hidden), nn.ReLU(), nn.Linear(hidden, classes))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


class DJINNFusion(nn.Module):
    """Sparse exact-relation DJINN with seven fixed relation groups."""

    def __init__(self, input_dim: int, classes: int, hidden: int = 20):
        super().__init__()
        self.input = nn.Linear(input_dim, hidden)
        self.self_scale = nn.Parameter(torch.ones(hidden))
        self.neighbor_scale = nn.Parameter(torch.zeros(hidden))
        self.relation_scale = nn.Parameter(torch.ones(len(KEY_TENSORS), hidden) * 0.1)
        self.mix_logits = nn.Parameter(torch.zeros(len(KEY_TENSORS) + 2))
        self.involution_gate = nn.Parameter(torch.ones(hidden))
        self.output = nn.Linear(hidden, classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.input(x)
        neigh = h[NEIGHBOR_TENSOR.to(x.device)].mean(dim=1)
        local = h * self.self_scale + neigh * self.neighbor_scale
        components = [local, h]
        for idx, key in enumerate(KEY_TENSORS):
            components.append(group_mean(local, key) * self.relation_scale[idx])
        weights = torch.softmax(self.mix_logits, dim=0)
        attended = sum(weights[idx] * part for idx, part in enumerate(components))
        gate = torch.tanh(self.involution_gate)
        z = torch.relu(local + gate * attended)
        return self.output(z)

    def folded_coefficients(self) -> dict[str, np.ndarray]:
        with torch.no_grad():
            return {
                "mix": torch.softmax(self.mix_logits, dim=0).cpu().numpy(),
                "gate": torch.tanh(self.involution_gate).cpu().numpy(),
            }


@dataclass
class QuantizedModel:
    state_dict: dict[str, torch.Tensor]
    scales: dict[str, float]
    raw_weight_bytes: int


def quantize_weights_int8(model: nn.Module) -> QuantizedModel:
    qstate = {}; scales = {}; raw = 0
    for name, value in model.state_dict().items():
        if value.is_floating_point():
            maximum = float(value.abs().max().item())
            scale = maximum / 127.0 if maximum else 1.0
            quant = torch.round(value / scale).clamp(-127, 127).to(torch.int8)
            qstate[name] = quant; scales[name] = scale; raw += quant.numel()
        else:
            qstate[name] = value.clone(); raw += value.numel() * value.element_size()
    return QuantizedModel(qstate, scales, raw)


def restore_weight_quantized(model: nn.Module, quantized: QuantizedModel) -> nn.Module:
    restored = copy.deepcopy(model)
    state = {name: (value.float() * quantized.scales[name] if value.dtype == torch.int8 else value)
             for name, value in quantized.state_dict.items()}
    restored.load_state_dict(state)
    return restored


def parameter_profile(model: nn.Module) -> dict[str, int]:
    parameters = sum(p.numel() for p in model.parameters())
    fixed_key_bytes = sum(k.numel() * 2 for k in KEY_TENSORS)
    neighbor_bytes = NEIGHBOR_TENSOR.numel() * 2
    return {
        "learnable_parameters": parameters,
        "float32_weight_bytes": parameters * 4,
        "int8_weight_bytes": parameters,
        "fixed_group_key_bytes_int16": fixed_key_bytes,
        "neighbor_index_bytes_int16": neighbor_bytes,
        "total_int8_plus_topology_bytes": parameters + fixed_key_bytes + neighbor_bytes,
    }
