"""
rcs_learner.py
Phase 4.3: Advanced RCS (Adaptive Recoil Compensation)

Learn weapon recoil patterns from actual mouse movement during fire.
"""

import json
import threading
from collections import deque
from pathlib import Path


class RCSLearner:
    """Learn and adapt RCS patterns per weapon."""
    
    def __init__(self, config_file="rcs_patterns.json", max_samples=100):
        self.config_file = Path(config_file)
        self.patterns = {}  # {weapon_name: [pattern]}
        self.max_samples = max_samples
        self._lock = threading.Lock()
        self.load_patterns()
    
    def load_patterns(self):
        """Load learned RCS patterns from disk."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    # Convert lists to deques
                    self.patterns = {
                        k: deque(v, maxlen=self.max_samples)
                        for k, v in data.items()
                    }
                    print(f"[RCS] Loaded {len(self.patterns)} weapon patterns")
            except Exception as e:
                print(f"[RCS] Error loading patterns: {e}")
    
    def save_patterns(self):
        """Save learned RCS patterns to disk."""
        try:
            with self._lock:
                save_data = {
                    k: list(v) for k, v in self.patterns.items()
                }
            with open(self.config_file, 'w') as f:
                json.dump(save_data, f, indent=2)
                print(f"[RCS] Saved {len(self.patterns)} patterns")
        except Exception as e:
            print(f"[RCS] Error saving: {e}")
    
    def record_recoil(self, weapon_name, recoil_data):
        """
        Record actual recoil data during fire.
        
        Args:
            weapon_name: Name of weapon (e.g., "ak47", "m4")
            recoil_data: List of (dy) values per frame during fire
        """
        with self._lock:
            if weapon_name not in self.patterns:
                self.patterns[weapon_name] = deque(maxlen=self.max_samples)
            
            self.patterns[weapon_name].append(recoil_data)
            print(f"[RCS] Recorded {weapon_name} pattern (sample {len(self.patterns[weapon_name])})")
    
    def get_pattern(self, weapon_name, default=None):
        """
        Get average RCS pattern for weapon.
        
        Args:
            weapon_name: Weapon to get pattern for
            default: Default pattern if not found
        
        Returns:
            List of recoil compensation values
        """
        with self._lock:
            if weapon_name not in self.patterns or not self.patterns[weapon_name]:
                return default or [0.5, 1.2, 1.8, 2.1, 1.9, 1.6, 1.3, 1.0, 0.8, 0.6, 0.4, 0.2, 0.1, 0.0]
            
            # Average all recorded patterns
            patterns_list = list(self.patterns[weapon_name])
            if not patterns_list:
                return default
            
            # Pad patterns to same length
            max_len = max(len(p) for p in patterns_list) if patterns_list else 14
            averaged = []
            
            for i in range(max_len):
                values = [
                    p[i] for p in patterns_list
                    if i < len(p)
                ]
                if values:
                    averaged.append(sum(values) / len(values))
                else:
                    averaged.append(0.0)
            
            return averaged
    
    def analyze_pattern(self, weapon_name):
        """Analyze pattern statistics for weapon."""
        with self._lock:
            if weapon_name not in self.patterns:
                return None
            
            patterns_list = list(self.patterns[weapon_name])
            if not patterns_list:
                return None
            
            return {
                'weapon': weapon_name,
                'samples': len(patterns_list),
                'avg_max_recoil': sum(max(p) for p in patterns_list) / len(patterns_list),
                'avg_pattern_length': sum(len(p) for p in patterns_list) / len(patterns_list)
            }


# Global instance
_rcs_learner = None


def initialize_rcs_learner():
    """Initialize RCS learner."""
    global _rcs_learner
    _rcs_learner = RCSLearner()
    return _rcs_learner


def get_rcs_learner():
    """Get global RCS learner instance."""
    return _rcs_learner


def get_rcs_pattern(weapon_name):
    """Get RCS pattern for weapon."""
    if _rcs_learner:
        return _rcs_learner.get_pattern(weapon_name)
    return None
