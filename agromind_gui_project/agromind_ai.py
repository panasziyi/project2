#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import lru_cache
from datetime import datetime
import random
from typing import Dict, Any, Tuple
import numpy as np
import openvino as ov

def _parse_iso_flexible(s: str) -> datetime:
    if not s:
        return datetime.now()
    try:
        if s.endswith("Z"):
            return datetime.fromisoformat(s.replace("Z", "+00:00"))
        return datetime.fromisoformat(s)
    except Exception:
        return datetime.now()

CROP_WATER_NEED = {
    "rice": 0.9,
    "corn": 0.6,
    "wheat": 0.5,
    "soybean": 0.55,
    "leafy": 0.7,
    "fruit": 0.65,
}

def estimate_growth_stage(crop: str, month: int) -> float:
    base = {"rice": (4, 9), "corn": (3, 8), "wheat": (11, 4), "soybean": (4, 9), "leafy": (1, 12), "fruit": (3, 10)}
    lo, hi = base.get(crop, (1, 12))
    if lo <= hi:
        stage = (month - lo) / max(1, (hi - lo))
    else:
        if month >= lo or month <= hi:
            span = (12 - lo + 1) + hi
            idx = (month - lo) if month >= lo else (12 - lo + 1) + month
            stage = idx / max(1, span)
        else:
            stage = 0.0
    return float(min(1.0, max(0.0, stage)))

def simulate_weather(location: str, seed: int = None) -> Dict[str, float]:
    if seed is None:
        seed = abs(hash(location)) % (2**31)
    rnd = random.Random(seed)
    temp = rnd.uniform(16, 34)
    humidity = rnd.uniform(45, 95)
    rainfall = max(0.0, rnd.gauss(5, 10))
    sunlight = rnd.uniform(2, 10)
    return {"temp": round(temp, 2), "humidity": round(humidity, 2), "rainfall": round(rainfall, 2), "sunlight": round(sunlight, 2)}

def build_feature_vector(crop: str, location: str, dt: datetime) -> Tuple[np.ndarray, Dict[str, float]]:
    weather = simulate_weather(location)
    growth_stage = estimate_growth_stage(crop, dt.month)
    water_need = CROP_WATER_NEED.get(crop, 0.6)
    x = np.array([[weather["temp"], weather["humidity"], weather["rainfall"], weather["sunlight"], growth_stage, water_need]], dtype=np.float32)
    return x, {**weather, "growth_stage": growth_stage, "crop_water_need": water_need}

@lru_cache(maxsize=1)
def get_compiled_model() -> Tuple[ov.CompiledModel, Dict[str, Any]]:
    core = ov.Core()
    ops = ov.opset8
    F, H, O = 6, 8, 2
    x = ops.parameter([1, F], ov.Type.f32, name="features")

    W1 = np.array([
        [ 0.06,  0.10,  0.02, -0.03, 0.12,  0.08],
        [-0.04,  0.07,  0.05,  0.06, 0.10, -0.02],
        [ 0.09, -0.08,  0.03,  0.02, 0.05,  0.04],
        [ 0.03,  0.01,  0.12, -0.04, 0.08,  0.06],
        [ 0.02,  0.05, -0.03,  0.07, 0.09,  0.01],
        [ 0.04,  0.06,  0.02,  0.05, 0.11,  0.03],
        [-0.02,  0.03,  0.08,  0.04, 0.07,  0.02],
        [ 0.05,  0.02,  0.06,  0.03, 0.10,  0.05],
    ], dtype=np.float32).T
    b1 = np.array([0.02, -0.01, 0.03, 0.00, 0.02, 0.01, -0.02, 0.01], dtype=np.float32)
    z1 = ops.matmul(x, ops.constant(W1, ov.Type.f32), False, False)
    z1b = ops.add(z1, ops.constant(b1, ov.Type.f32))
    a1 = ops.relu(z1b)

    W2 = np.array([
        [ 0.18, -0.06, 0.07,  0.09, 0.05,  0.04, 0.02, 0.03],
        [ 0.12,  0.08, 0.06, -0.05, 0.07, -0.02, 0.04, 0.05],
    ], dtype=np.float32).T
    b2 = np.array([0.01, 0.02], dtype=np.float32)
    z2 = ops.matmul(a1, ops.constant(W2, ov.Type.f32), False, False)
    z2b = ops.add(z2, ops.constant(b2, ov.Type.f32))

    neg = ops.multiply(z2b, ops.constant(np.array([-1.0], dtype=np.float32), ov.Type.f32))
    y = ops.divide(ops.constant(np.array([1.0], dtype=np.float32), ov.Type.f32), ops.add(ops.exp(neg), ops.constant(np.array([1.0], dtype=np.float32), ov.Type.f32)))

    model = ov.Model([y], [x], "AgroMind_MLP")
    compiled = core.compile_model(model, "CPU")
    return compiled, {"input_name": compiled.input(0).get_any_name(), "output_name": compiled.output(0).get_any_name()}

def postprocess(scores: np.ndarray) -> Dict[str, Any]:
    irr, fert = float(scores[0, 0]), float(scores[0, 1])
    def label(v: float, lo=0.35, hi=0.65) -> str:
        return "高" if v >= hi else ("低" if v <= lo else "中")
    irrigation_label = label(irr)
    fertilization_label = label(fert)
    return {
        "irrigation_score": irr,
        "fertilization_score": fert,
        "irrigation_level": irrigation_label,
        "fertilization_level": fertilization_label,
        "irrigation_advice": {"高":"建議安排灌溉：分次、避免積水。","中":"視土壤狀況少量多次。","低":"暫不灌溉，持續觀察。"}[irrigation_label],
        "fertilization_advice": {"高":"建議補充肥分：以氮/鉀為主，避免過量。","中":"可少量複合肥，視葉色與生長勢調整。","低":"暫不施肥，以觀測為主。"}[fertilization_label],
    }

def recommend(crop: str, location: str, date_iso: str = None) -> Dict[str, Any]:
    crop_key = (crop or "").strip().lower()
    if crop_key not in CROP_WATER_NEED:
        return {"ok": False, "error": f"不支援的作物'{crop}'. 請使用其中之一: {', '.join(CROP_WATER_NEED.keys())}"}
    dt = _parse_iso_flexible(date_iso) if date_iso else datetime.now()
    feats, context = build_feature_vector(crop_key, location.strip(), dt)
    compiled, _ = get_compiled_model()
    try:
        y = compiled([feats])[0]
    except Exception:
        ir = compiled.create_infer_request()
        ir.infer({0: feats})
        y = ir.get_output_tensor(0).data
    rec = postprocess(y)
    return {"ok": True, "input": {"crop": crop_key, "location": location, "date": dt.isoformat(timespec="seconds")}, "context": context, "model_scores": rec}
