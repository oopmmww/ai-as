"""
data_logger.py
ระบบเก็บข้อมูลการทำงานที่ครบครัน สำหรับวิเคราะห์และพัฒนาต่อยอด

เก็บข้อมูล:
- ตรวจจับ (Detection): ตำแหน่ง ขนาด คะแนน
- ประสิทธิภาพ (Performance): FPS Latency Memory
- เหตุการณ์ (Events): เมื่อไรตรวจจับ เมื่อไรเสีย
- สภาพแวดล้อม (Environment): แสง FPS ปัจจัยอื่น
"""

import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from collections import deque
import psutil
import os


class DetectionLogger:
    """บันทึกข้อมูลการตรวจจับทั้งหมด"""
    
    def __init__(self, max_history=10000):
        self.max_history = max_history
        self.detections = deque(maxlen=max_history)
        self._lock = threading.Lock()
    
    def log_detection(self, frame_number, bbox, confidence, 
                      detection_type, outlier_reasons=None):
        """
        บันทึกการตรวจจับ
        
        Args:
            frame_number: เฟรมที่เท่าไหร่
            bbox: (x, y, w, h)
            confidence: ค่า 0-1
            detection_type: 'valid', 'rejected', 'predicted'
            outlier_reasons: เหตุผลที่ปฏิเสธ (ถ้าเป็น rejected)
        """
        with self._lock:
            entry = {
                'timestamp': datetime.now().isoformat(),
                'frame_number': frame_number,
                'bbox': bbox,
                'confidence': round(float(confidence), 3),
                'detection_type': detection_type,
                'outlier_reasons': outlier_reasons or []
            }
            self.detections.append(entry)
    
    def get_stats(self):
        """สถิติการตรวจจับ"""
        with self._lock:
            if not self.detections:
                return {}
            
            valid = sum(1 for d in self.detections if d['detection_type'] == 'valid')
            rejected = sum(1 for d in self.detections if d['detection_type'] == 'rejected')
            predicted = sum(1 for d in self.detections if d['detection_type'] == 'predicted')
            
            confidences = [d['confidence'] for d in self.detections if d['detection_type'] == 'valid']
            
            return {
                'total': len(self.detections),
                'valid': valid,
                'rejected': rejected,
                'predicted': predicted,
                'rejection_rate': f"{rejected / (valid + rejected) * 100:.1f}%" if (valid + rejected) > 0 else "N/A",
                'avg_confidence': round(sum(confidences) / len(confidences), 3) if confidences else 0,
                'min_confidence': round(min(confidences), 3) if confidences else 0,
                'max_confidence': round(max(confidences), 3) if confidences else 0,
            }
    
    def get_recent(self, count=100):
        """ดึง 100 ครั้งล่าสุด"""
        with self._lock:
            return list(self.detections)[-count:]


class PerformanceLogger:
    """บันทึกประสิทธิภาพระบบ"""
    
    def __init__(self, window_size=60):
        self.window_size = window_size
        self.fps_history = deque(maxlen=window_size)
        self.latency_history = deque(maxlen=window_size)  # ms
        self.memory_history = deque(maxlen=window_size)  # MB
        self._lock = threading.Lock()
        self.process = psutil.Process(os.getpid())
    
    def log_frame(self, fps, latency_ms):
        """
        บันทึกข้อมูลต่อเฟรม
        
        Args:
            fps: frames per second
            latency_ms: เวลา vision loop (millisecond)
        """
        with self._lock:
            self.fps_history.append(fps)
            self.latency_history.append(latency_ms)
            
            try:
                memory_mb = self.process.memory_info().rss / (1024 * 1024)
                self.memory_history.append(memory_mb)
            except:
                pass
    
    def get_stats(self):
        """สถิติประสิทธิภาพ"""
        with self._lock:
            if not self.fps_history:
                return {}
            
            return {
                'current_fps': round(self.fps_history[-1], 1) if self.fps_history else 0,
                'avg_fps': round(sum(self.fps_history) / len(self.fps_history), 1),
                'min_fps': round(min(self.fps_history), 1),
                'max_fps': round(max(self.fps_history), 1),
                
                'current_latency_ms': round(self.latency_history[-1], 2) if self.latency_history else 0,
                'avg_latency_ms': round(sum(self.latency_history) / len(self.latency_history), 2),
                'max_latency_ms': round(max(self.latency_history), 2),
                
                'current_memory_mb': round(self.memory_history[-1], 1) if self.memory_history else 0,
                'peak_memory_mb': round(max(self.memory_history), 1) if self.memory_history else 0,
            }


class EventLogger:
    """บันทึกเหตุการณ์สำคัญ"""
    
    def __init__(self, max_history=1000):
        self.max_history = max_history
        self.events = deque(maxlen=max_history)
        self._lock = threading.Lock()
    
    def log_event(self, event_type, severity, message, data=None):
        """
        บันทึกเหตุการณ์
        
        Args:
            event_type: 'detection_lost', 'mog2_ready', 'confidence_low', etc.
            severity: 'info', 'warning', 'error'
            message: ข้อความอธิบาย
            data: ข้อมูลเพิ่มเติม (dict)
        """
        with self._lock:
            entry = {
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type,
                'severity': severity,
                'message': message,
                'data': data or {}
            }
            self.events.append(entry)
    
    def get_recent(self, count=100):
        """ดึง 100 เหตุการณ์ล่าสุด"""
        with self._lock:
            return list(self.events)[-count:]
    
    def get_by_type(self, event_type, count=50):
        """ดึงเหตุการณ์ตามประเภท"""
        with self._lock:
            filtered = [e for e in self.events if e['event_type'] == event_type]
            return filtered[-count:]


class EnvironmentLogger:
    """บันทึกข้อมูลสภาพแวดล้อม (แสง ฉากหลัง ฯลฯ)"""
    
    def __init__(self, max_history=500):
        self.max_history = max_history
        self.samples = deque(maxlen=max_history)
        self._lock = threading.Lock()
    
    def log_sample(self, frame_number, brightness, contrast, 
                   fg_pixels_ratio=None, target_count=0, mog2_learning_complete=False):
        """
        บันทึกตัวอย่างสภาพแวดล้อม
        
        Args:
            frame_number: เฟรมที่เท่าไหร่
            brightness: ความสว่าง 0-255
            contrast: ความเปรียบต่าง 0-255
            fg_pixels_ratio: สัดส่วน foreground pixels (0-1)
            target_count: จำนวนเป้าหมายที่ตรวจจับได้
            mog2_learning_complete: MOG2 เรียนรู้เสร็จหรือยัง
        """
        with self._lock:
            entry = {
                'timestamp': datetime.now().isoformat(),
                'frame_number': frame_number,
                'brightness': int(brightness),
                'contrast': int(contrast),
                'fg_pixels_ratio': round(float(fg_pixels_ratio), 4) if fg_pixels_ratio is not None else None,
                'target_count': int(target_count),
                'mog2_learning_complete': bool(mog2_learning_complete)
            }
            self.samples.append(entry)
    
    def get_recent(self, count=100):
        """ดึง 100 ตัวอย่างล่าสุด"""
        with self._lock:
            return list(self.samples)[-count:]


class SessionLogger:
    """เซสชันการทำงานทั้งหมด (รวม detection, performance, events)"""
    
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.session_start = datetime.now()
        self.session_id = self.session_start.strftime("%Y%m%d_%H%M%S")
        
        self.detection_logger = DetectionLogger()
        self.performance_logger = PerformanceLogger()
        self.event_logger = EventLogger()
        self.environment_logger = EnvironmentLogger()
        
        self._lock = threading.Lock()
        self._save_thread = None
        self._stop_save = threading.Event()
    
    def start_auto_save(self, interval_seconds=60):
        """เริ่มบันทึกอัตโนมัติทุก X วินาที"""
        self._stop_save.clear()
        self._save_thread = threading.Thread(
            target=self._auto_save_loop,
            args=(interval_seconds,),
            daemon=True,
            name="DataLoggerAutoSave"
        )
        self._save_thread.start()
    
    def _auto_save_loop(self, interval_seconds):
        """Loop สำหรับบันทึกอัตโนมัติ"""
        while not self._stop_save.is_set():
            time.sleep(interval_seconds)
            if not self._stop_save.is_set():
                self.save_session()
    
    def save_session(self):
        """บันทึกข้อมูลทั้งหมดลง JSON"""
        try:
            session_file = self.log_dir / f"session_{self.session_id}.json"
            
            data = {
                'session_id': self.session_id,
                'session_start': self.session_start.isoformat(),
                'session_duration_sec': (datetime.now() - self.session_start).total_seconds(),
                'saved_at': datetime.now().isoformat(),
                
                'detection_stats': self.detection_logger.get_stats(),
                'performance_stats': self.performance_logger.get_stats(),
                
                'recent_detections': self.detection_logger.get_recent(200),
                'recent_events': self.event_logger.get_recent(100),
                'recent_environment': self.environment_logger.get_recent(100),
            }
            
            with open(session_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"[LOG ERROR] Failed to save session: {e}")
            return False
    
    def stop_and_save(self):
        """หยุดบันทึกและบันทึกไฟล์สุดท้าย"""
        self._stop_save.set()
        if self._save_thread:
            self._save_thread.join(timeout=5)
        return self.save_session()
    
    def export_csv(self):
        """ส่งออก CSV สำหรับวิเคราะห์ใน Excel/Pandas"""
        import csv
        
        try:
            # Export detections
            detections_file = self.log_dir / f"detections_{self.session_id}.csv"
            with open(detections_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'timestamp', 'frame_number', 'x', 'y', 'w', 'h',
                    'confidence', 'detection_type', 'outlier_reasons'
                ])
                writer.writeheader()
                for d in self.detection_logger.detections:
                    x, y, w, h = d['bbox'] or (0, 0, 0, 0)
                    writer.writerow({
                        'timestamp': d['timestamp'],
                        'frame_number': d['frame_number'],
                        'x': x, 'y': y, 'w': w, 'h': h,
                        'confidence': d['confidence'],
                        'detection_type': d['detection_type'],
                        'outlier_reasons': '; '.join(d['outlier_reasons'])
                    })
            
            # Export performance
            perf_file = self.log_dir / f"performance_{self.session_id}.csv"
            with open(perf_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['fps', 'latency_ms', 'memory_mb'])
                for fps, lat, mem in zip(
                    self.performance_logger.fps_history,
                    self.performance_logger.latency_history,
                    self.performance_logger.memory_history
                ):
                    writer.writerow([fps, lat, mem])
            
            return True
        except Exception as e:
            print(f"[LOG ERROR] Failed to export CSV: {e}")
            return False


# Global instances
_global_session_logger = None


def initialize_logger(log_dir="logs"):
    """เริ่มต้นระบบ logging (เรียกใน main.py)"""
    global _global_session_logger
    _global_session_logger = SessionLogger(log_dir)
    _global_session_logger.start_auto_save(interval_seconds=60)
    print(f"[LOGGER] Initialized - Session: {_global_session_logger.session_id}")
    return _global_session_logger


def get_logger():
    """ดึง global logger instance"""
    return _global_session_logger


def log_detection(frame_number, bbox, confidence, detection_type, outlier_reasons=None):
    """Convenience function"""
    from config import config
    if not config.LOGGING_ENABLED:
        return
    if _global_session_logger:
        _global_session_logger.detection_logger.log_detection(
            frame_number, bbox, confidence, detection_type, outlier_reasons
        )


def log_event(event_type, severity, message, data=None):
    """Convenience function"""
    from config import config
    if not config.LOGGING_ENABLED:
        return
    if _global_session_logger:
        _global_session_logger.event_logger.log_event(event_type, severity, message, data)


def log_frame(fps, latency_ms):
    """Convenience function"""
    from config import config
    if not config.LOGGING_ENABLED:
        return
    if _global_session_logger:
        _global_session_logger.performance_logger.log_frame(fps, latency_ms)


def log_environment(frame_number, brightness, contrast, fg_pixels_ratio=None, 
                    target_count=0, mog2_learning_complete=False):
    """Convenience function"""
    from config import config
    if not config.LOGGING_ENABLED:
        return
    if _global_session_logger:
        _global_session_logger.environment_logger.log_sample(
            frame_number, brightness, contrast, fg_pixels_ratio, 
            target_count, mog2_learning_complete
        )
