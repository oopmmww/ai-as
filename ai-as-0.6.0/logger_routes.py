"""
logger_routes.py
Flask endpoints สำหรับดูและส่งออกข้อมูลที่เก็บ

Endpoints:
GET  /api/logger/stats          - สถิติทั้งหมด
GET  /api/logger/detections     - ข้อมูลการตรวจจับ
GET  /api/logger/events         - เหตุการณ์
GET  /api/logger/performance    - ประสิทธิภาพ
GET  /api/logger/environment    - สภาพแวดล้อม
POST /api/logger/export-csv     - ส่งออก CSV
POST /api/logger/save           - บันทึกข้อมูลทำนที
"""

from flask import Blueprint, jsonify, request, send_file
import data_logger as logger
import io
import csv

logger_bp = Blueprint('logger', __name__, url_prefix='/api/logger')


@logger_bp.route('/stats', methods=['GET'])
def get_all_stats():
    """ดึงสถิติทั้งหมด"""
    session_logger = logger.get_logger()
    if not session_logger:
        return jsonify({'error': 'Logger not initialized'}), 500
    
    return jsonify({
        'session_id': session_logger.session_id,
        'session_start': session_logger.session_start.isoformat(),
        'session_duration_sec': (
            __import__('datetime').datetime.now() - session_logger.session_start
        ).total_seconds(),
        
        'detection': session_logger.detection_logger.get_stats(),
        'performance': session_logger.performance_logger.get_stats(),
        'environment_samples': len(session_logger.environment_logger.samples),
        'events': len(session_logger.event_logger.events),
    })


@logger_bp.route('/detections', methods=['GET'])
def get_detections():
    """ดึงข้อมูลการตรวจจับ (สามารถ limit และ offset)"""
    session_logger = logger.get_logger()
    if not session_logger:
        return jsonify({'error': 'Logger not initialized'}), 500
    
    limit = request.args.get('limit', default=100, type=int)
    
    detections = session_logger.detection_logger.get_recent(limit)
    
    return jsonify({
        'count': len(detections),
        'detections': detections
    })


@logger_bp.route('/detections/by-type/<detection_type>', methods=['GET'])
def get_detections_by_type(detection_type):
    """ดึงการตรวจจับตามประเภท (valid/rejected/predicted)"""
    session_logger = logger.get_logger()
    if not session_logger:
        return jsonify({'error': 'Logger not initialized'}), 500
    
    limit = request.args.get('limit', default=50, type=int)
    
    detections = [
        d for d in session_logger.detection_logger.detections
        if d['detection_type'] == detection_type
    ][-limit:]
    
    return jsonify({
        'count': len(detections),
        'type': detection_type,
        'detections': detections
    })


@logger_bp.route('/detections/low-confidence', methods=['GET'])
def get_low_confidence_detections():
    """ดึงการตรวจจับที่มีคะแนนต่ำ (< 0.5)"""
    session_logger = logger.get_logger()
    if not session_logger:
        return jsonify({'error': 'Logger not initialized'}), 500
    
    low_conf = [
        d for d in session_logger.detection_logger.detections
        if d['confidence'] < 0.5 and d['detection_type'] == 'valid'
    ]
    
    return jsonify({
        'count': len(low_conf),
        'detections': low_conf[-100:]
    })


@logger_bp.route('/events', methods=['GET'])
def get_events():
    """ดึงเหตุการณ์"""
    session_logger = logger.get_logger()
    if not session_logger:
        return jsonify({'error': 'Logger not initialized'}), 500
    
    limit = request.args.get('limit', default=100, type=int)
    severity = request.args.get('severity', default=None)  # 'error', 'warning', 'info'
    
    events = session_logger.event_logger.get_recent(limit)
    
    if severity:
        events = [e for e in events if e['severity'] == severity]
    
    return jsonify({
        'count': len(events),
        'events': events
    })


@logger_bp.route('/events/<event_type>', methods=['GET'])
def get_events_by_type(event_type):
    """ดึงเหตุการณ์ตามประเภท"""
    session_logger = logger.get_logger()
    if not session_logger:
        return jsonify({'error': 'Logger not initialized'}), 500
    
    limit = request.args.get('limit', default=50, type=int)
    events = session_logger.event_logger.get_by_type(event_type, limit)
    
    return jsonify({
        'count': len(events),
        'type': event_type,
        'events': events
    })


@logger_bp.route('/performance', methods=['GET'])
def get_performance():
    """ดึงข้อมูลประสิทธิภาพ"""
    session_logger = logger.get_logger()
    if not session_logger:
        return jsonify({'error': 'Logger not initialized'}), 500
    
    return jsonify({
        'stats': session_logger.performance_logger.get_stats(),
        'fps_history': list(session_logger.performance_logger.fps_history)[-60:],
        'latency_history': list(session_logger.performance_logger.latency_history)[-60:],
        'memory_history': list(session_logger.performance_logger.memory_history)[-60:]
    })


@logger_bp.route('/environment', methods=['GET'])
def get_environment():
    """ดึงข้อมูลสภาพแวดล้อม"""
    session_logger = logger.get_logger()
    if not session_logger:
        return jsonify({'error': 'Logger not initialized'}), 500
    
    limit = request.args.get('limit', default=100, type=int)
    samples = session_logger.environment_logger.get_recent(limit)
    
    return jsonify({
        'count': len(samples),
        'samples': samples
    })


@logger_bp.route('/export-csv', methods=['POST'])
def export_csv():
    """ส่งออกข้อมูลเป็น CSV"""
    session_logger = logger.get_logger()
    if not session_logger:
        return jsonify({'error': 'Logger not initialized'}), 500
    
    if session_logger.export_csv():
        return jsonify({
            'status': 'success',
            'message': f"Exported to logs/ - detections_{session_logger.session_id}.csv"
        })
    else:
        return jsonify({'error': 'Export failed'}), 500


@logger_bp.route('/save', methods=['POST'])
def manual_save():
    """บันทึกข้อมูลด้วยตนเอง (นอกเหนือจากอัตโนมัติ)"""
    session_logger = logger.get_logger()
    if not session_logger:
        return jsonify({'error': 'Logger not initialized'}), 500
    
    if session_logger.save_session():
        return jsonify({
            'status': 'success',
            'message': f"Saved session_{session_logger.session_id}.json"
        })
    else:
        return jsonify({'error': 'Save failed'}), 500


@logger_bp.route('/detection-summary', methods=['GET'])
def get_detection_summary():
    """สรุปข้อมูลการตรวจจับ (รวม stats และ outlier breakdown)"""
    session_logger = logger.get_logger()
    if not session_logger:
        return jsonify({'error': 'Logger not initialized'}), 500
    
    # นับเหตุผลการปฏิเสธ
    outlier_reasons = {}
    for detection in session_logger.detection_logger.detections:
        if detection['detection_type'] == 'rejected':
            for reason in detection['outlier_reasons']:
                outlier_reasons[reason] = outlier_reasons.get(reason, 0) + 1
    
    # ความเป็นไปได้ที่จะตรวจจับ (ตรวจจับสำเร็จ / ทั้งหมด)
    stats = session_logger.detection_logger.get_stats()
    
    return jsonify({
        'stats': stats,
        'outlier_breakdown': outlier_reasons,
        'top_rejection_reasons': sorted(
            outlier_reasons.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
    })


@logger_bp.route('/performance-summary', methods=['GET'])
def get_performance_summary():
    """สรุปประสิทธิภาพ (ความเสี่ยง ความสุดขั้ว ฯลฯ)"""
    session_logger = logger.get_logger()
    if not session_logger:
        return jsonify({'error': 'Logger not initialized'}), 500
    
    perf = session_logger.performance_logger
    stats = perf.get_stats()
    
    # นับ frames ที่มี FPS ต่ำ (< 30)
    low_fps_count = sum(1 for f in perf.fps_history if f < 30)
    
    # นับ frames ที่มี latency สูง (> 30ms)
    high_latency_count = sum(1 for l in perf.latency_history if l > 30)
    
    return jsonify({
        'stats': stats,
        'low_fps_frames': low_fps_count,
        'high_latency_frames': high_latency_count,
        'health': 'good' if low_fps_count < 5 and high_latency_count < 5 else 'warning'
    })


# Helper: ใช้ใน main.py
@logger_bp.route('/trigger-stats', methods=['GET'])
def get_trigger_stats():
    """ดึงข้อมูลสถิติการกดยิง"""
    session_logger = logger.get_logger()
    if not session_logger:
        return jsonify({'error': 'Logger not initialized'}), 500
    
    # นับการกดยิงที่สำเร็จ
    trigger_fires = [
        e for e in session_logger.event_logger.events
        if e['event_type'] == 'trigger_fire'
    ]
    
    # นับ target lost
    target_lost = [
        e for e in session_logger.event_logger.events
        if e['event_type'] == 'target_lost'
    ]
    
    # นับ Arduino errors
    arduino_errors = [
        e for e in session_logger.event_logger.events
        if 'arduino' in e['event_type'] and 'error' in e['event_type']
    ]
    
    return jsonify({
        'trigger_fires': len(trigger_fires),
        'target_lost_count': len(target_lost),
        'arduino_errors': len(arduino_errors),
        'recent_fires': trigger_fires[-5:],  # 5 ครั้งล่าสุด
    })


@logger_bp.route('/health-check', methods=['GET'])
def get_health_check():
    """ดึงสภาพสุขภาพระบบ"""
    session_logger = logger.get_logger()
    if not session_logger:
        return jsonify({'error': 'Logger not initialized'}), 500
    
    perf = session_logger.performance_logger.get_stats()
    det = session_logger.detection_logger.get_stats()
    
    # ตรวจสุขภาพ
    issues = []
    
    # FPS ต่ำ
    if perf.get('current_fps', 0) < 30:
        issues.append('Low FPS detected')
    
    # Latency สูง
    if perf.get('current_latency_ms', 0) > 50:
        issues.append('High latency detected')
    
    # Rejection rate สูง
    if 'rejection_rate' in det:
        try:
            rate = float(det['rejection_rate'].rstrip('%'))
            if rate > 50:
                issues.append('High rejection rate')
        except:
            pass
    
    # Arduino errors
    errors = [
        e for e in session_logger.event_logger.events
        if 'error' in e['event_type']
    ]
    
    if len(errors) > 10:
        issues.append(f'Multiple errors ({len(errors)})')
    
    return jsonify({
        'status': 'warning' if issues else 'good',
        'issues': issues,
        'performance': perf,
        'detection': det,
        'errors_count': len(errors),
    })


def register_logger_routes(app):
    """ลงทะเบียน logger routes ใน Flask app"""
    app.register_blueprint(logger_bp)
