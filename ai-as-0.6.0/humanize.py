import numpy as np
import random
import math
import time as time_module
from config import config

# Try to use better noise library, fallback to basic Perlin
try:
    from noise import snoise2
    USE_OPENSIMPLEX = True
    print("✅ OpenSimplex noise available")
except ImportError:
    USE_OPENSIMPLEX = False
    print("⚠️ Using Perlin fallback (pip install noise for better quality)")
    
    # Fallback: basic Perlin
    _perm = list(range(256))
    random.shuffle(_perm)
    _perm *= 2
    
    def _fade(t): return t*t*t*(t*(t*6-15)+10)
    def _grad(h, x): return x if (h&3)<2 else -x
    def _perlin(x):
        xi = int(math.floor(x)) & 255
        xf = x - math.floor(x)
        u  = _fade(xf)
        a = _grad(_perm[xi], xf)
        b = _grad(_perm[xi+1], xf-1)
        return a + u * (b - a)

# ── Noise generators ─────────────────────────────────────
def _get_opensimplex_noise(t: float, seed: int) -> float:
    """High-quality fractal brownian motion using OpenSimplex.
    
    คำนวณ FBM (Fractal Brownian Motion) ด้วยตัวเอง 3 octaves
    เพราะ snoise2() รับแค่ (x, y) ไม่รับ octaves/persistence โดยตรง
    """
    value = 0.0
    amplitude = 1.0
    frequency = 1.0
    max_value = 0.0

    for i in range(3):  # 3 octaves for detail
        try:
            value += snoise2(
                t * frequency + seed,   # x
                i * 0.5                 # y offset ต่างกันต่อ octave
            ) * amplitude
        except Exception:
            pass
        max_value += amplitude
        amplitude *= 0.5   # persistence = 0.5
        frequency *= 2.0   # lacunarity = 2.0

    return value / max_value if max_value > 0 else 0.0

def _get_perlin_noise(t: float, seed: int) -> float:
    """Fallback Perlin noise (weaker than OpenSimplex)."""
    return _perlin(t * 2.0 + seed * 0.1)

# ── Bezier micro-curve ───────────────────────────────────
def _bezier(dx, dy, s):
    """Create smooth Bezier curve deviation."""
    d = (dx*dx + dy*dy)**0.5
    if d < 0.5:
        return dx, dy
    
    # Perpendicular vector
    px, py = -dy/d, dx/d
    
    # Random control point magnitude
    ca = random.uniform(-0.4, 0.4) * s * min(d*0.08, 1.5)
    
    # Bezier control point
    mx = dx*0.5 + px*ca
    my = dy*0.5 + py*ca
    
    # Quadratic Bezier interpolation
    return 2*mx - dx*0.5, 2*my - dy*0.5

# ── Helper ───────────────────────────────────────────────
def _strength() -> float:
    """Get humanize strength from config."""
    if hasattr(config, "HUMAN_STR"):
        return config.HUMAN_STR
    return getattr(config, "HUMAN_STRENGTH", 1.0)

# ── Main humanize function ───────────────────────────────
def humanize_movement(dx: float, dy: float, confidence: float = 1.0) -> tuple:
    """Apply natural-looking humanization to mouse movement.
    
    ✨ NEW: confidence-aware humanization
    - High confidence (>0.7): Full humanize (natural looking)
    - Medium confidence (0.5-0.7): Medium humanize
    - Low confidence (<0.5): Minimal humanize (precise)
    
    Distance-based zones:
    - <0.5px: return zero (too small)
    - <3px: pass-through (already natural)
    - <8px: light Gaussian noise
    - >=8px: full humanize (noise + Bezier + stutter)
    """
    
    if not config.HUMANIZE:
        return int(dx), int(dy)

    dist = (dx*dx + dy*dy)**0.5
    if dist < 0.5:
        return 0, 0

    s = _strength()
    t = time_module.time()
    
    # ✨ Confidence-based strength modifier
    # High confidence (0.7+) = use full strength
    # Low confidence (0.4) = reduce humanize to be more precise
    confidence_factor = max(0.3, min(1.0, (confidence - 0.4) / 0.3))  # 0.4→0.3, 0.7→1.0

    # ─ ZONE 1: Very close (<3px) - no humanize needed ─
    if dist < 3.0:
        return int(round(dx)), int(round(dy))

    # ─ ZONE 2: Close (3-8px) - minimal noise only ─
    if dist < 8.0:
        sigma = 0.05 * s * confidence_factor
        dx += np.random.normal(0, sigma)
        dy += np.random.normal(0, sigma)
        return int(round(dx)), int(round(dy))

    # ─ ZONE 3: Far (≥8px) - FULL HUMANIZE ─
    dfac = min(dist / 25.0, 1.0)
    sigma = (0.2 + dfac * 0.95) * s * confidence_factor

    # Step 1: Add fractal noise (confidence-aware)
    if USE_OPENSIMPLEX:
        noise_x = _get_opensimplex_noise(t * 2.0, 0)
        noise_y = _get_opensimplex_noise(t * 2.0, 100)
    else:
        noise_x = _get_perlin_noise(t * 2.0, 0)
        noise_y = _get_perlin_noise(t * 2.0, 100)
    
    dx += noise_x * sigma * 1.2
    dy += noise_y * sigma * 1.2
    
    # Step 2: Add Gaussian noise
    dx += np.random.normal(0, sigma * 0.3)
    dy += np.random.normal(0, sigma * 0.3)

    # Step 3: Bezier curves - confidence-aware probability
    if dist > 12:
        # Low confidence = less Bezier (be more direct)
        # High confidence = more Bezier (look natural)
        base_prob = min(0.55, 0.25 + (dist - 12) / 80.0)
        prob = base_prob * (0.5 + 0.5 * confidence_factor)  # 0.5x to 1.0x
        
        if random.random() < prob:
            dx, dy = _bezier(dx, dy, s * confidence_factor)

    # Step 4: Micro-stutter - confidence-aware frequency
    stutter_chance = 0.15 * confidence_factor  # Reduce stutter if low confidence
    
    if random.random() < stutter_chance:
        if random.random() < 0.6:  # 60% = full frame pause
            return 0, 0
        else:  # 40% = slow frame
            k = random.uniform(0.65, 0.85)
            dx *= k
            dy *= k

    # Step 5: CAP CALCULATION - confidence-aware
    # High confidence: more permissive cap (allow larger movements)
    # Low confidence: tighter cap (smoother aim)
    base_cap = max(3.0, dist * 0.4 + 2.0)
    strength_factor = 1.0 + (s - 1.0) * 0.15
    
    # Confidence affects cap: high conf = higher cap (more natural), low conf = lower cap (precise)
    cap_factor = 0.7 + 0.3 * confidence_factor  # 0.7 to 1.0
    cap = base_cap * strength_factor * cap_factor
    cap = np.clip(cap, 3.0, 60.0)

    return (
        int(round(float(np.clip(dx, -cap, cap)))),
        int(round(float(np.clip(dy, -cap, cap))))
    )
