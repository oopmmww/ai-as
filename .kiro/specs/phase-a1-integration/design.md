# Design: Phase A1 Integration

## High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Flask Application                   │
│                    (main.py)                         │
└────────────────┬────────────────────────────────────┘
                 │
      ┌──────────┼──────────┐
      │          │          │
      ▼          ▼          ▼
  Vision.py   Routes   Dashboard
   (detect)   (API)      (UI)
      │          │          │
      └──────────┼──────────┘
                 │
                 ▼
         Logger System
    ┌────────────────────┐
    │  data_logger.py    │
    │  ┌──────────────┐  │
    │  │ Detection    │  │
    │  │ Performance  │  │
    │  │ Environment  │  │
    │  │ Event        │  │
    │  └──────────────┘  │
    │      (JSON)        │
    └────────────────────┘
```

## Integration Flow

### 1. main.py Initialization Sequence

```
1. Pre-flight checks (hardware, config)
2. Initialize Flask app
3. Import logger modules
4. Initialize logger: initialize_logger(log_dir="logs")
5. Register logger routes: register_logger_routes(app)
6. Register dashboard route: register_dashboard_route(app)
7. Start vision thread
8. Start Flask app
9. Register cleanup handler
```

### 2. Data Flow During Execution

```
Vision Loop (vision.py)
    ├─ Capture frame
    ├─ log_frame(fps, latency_ms)
    ├─ Perform detection
    ├─ log_detection(...) [valid/rejected]
    ├─ Every 60 frames: log_environment(...)
    ├─ On events: log_event(...)
    └─ Continue

Logger System
    ├─ Accumulate data in memory
    ├─ Auto-save to JSON every 60 seconds
    └─ Serve via API endpoints

Dashboard/API
    ├─ Query logger data
    ├─ Display real-time metrics
    └─ Provide export/analysis
```

### 3. Shutdown Sequence

```
User closes app
    │
    ▼
Keyboard interrupt / window close
    │
    ▼
atexit handler triggered
    │
    ▼
_cleanup() called
    │
    ├─ Stop vision thread
    ├─ Call logger_instance.stop_and_save()
    └─ Exit gracefully
```

## Implementation Components

### Component 1: main.py Modifications

**File**: `c:\Users\kitatar52\Downloads\aias\main.py`

**Changes**:
- Add imports: `data_logger`, `logger_routes`, `dashboard_route`
- Add initialization before `app.run()`:
  ```python
  initialize_logger(log_dir="logs")
  register_logger_routes(app)
  register_dashboard_route(app)
  ```
- Update `_cleanup()`:
  ```python
  logger_instance.stop_and_save()
  ```
- Update `_open_browser()` to open dashboard instead of index

### Component 2: vision.py Logging Integration

**File**: `c:\Users\kitatar52\Downloads\aias\vision.py`

**Changes**:
- Add import: `from data_logger import log_detection, log_event, log_frame, log_environment`
- In `vision_loop()`:
  - Add `log_frame(fps, latency_ms)` after each frame
  - Add `log_detection(...)` for valid/rejected detections
  - Add `log_environment(...)` every 60 frames
  - Add `log_event(...)` for critical events

### Component 3: Logger Data Persistence

**File**: `c:\Users\kitatar52\Downloads\aias\data_logger.py`

**Already implemented** - No changes needed:
- `initialize_logger()` - Sets up logger instance
- `stop_and_save()` - Persists data to JSON
- All logging convenience functions

### Component 4: API Routes

**File**: `c:\Users\kitatar52\Downloads\aias\logger_routes.py`

**Already implemented** - No changes needed:
- 15+ API endpoints for data access
- Statistics aggregation
- CSV export functionality

### Component 5: Dashboard UI & Route

**Files**: 
- `c:\Users\kitatar52\Downloads\aias\templates\dashboard.html`
- `c:\Users\kitatar52\Downloads\aias\dashboard_route.py`

**Already implemented** - No changes needed:
- Real-time dashboard with 4 graphs
- Statistics cards
- Rejection breakdown analysis
- Recent events log
- Action buttons

## Data Structures

### Logger JSON Output Structure

```json
{
  "session": {
    "start_time": "2026-10-09T10:30:00",
    "duration_seconds": 300,
    "frame_count": 9000
  },
  "detections": [
    {
      "frame_number": 100,
      "bbox": [x, y, w, h],
      "confidence": 0.92,
      "type": "valid/rejected",
      "reasons": ["reason1", "reason2"]
    }
  ],
  "performance": [
    {
      "frame_number": 100,
      "fps": 30.0,
      "latency_ms": 33.3,
      "memory_mb": 512
    }
  ],
  "events": [
    {
      "timestamp": "2026-10-09T10:30:05",
      "type": "mog2_ready",
      "severity": "info",
      "data": {}
    }
  ],
  "environment": [
    {
      "frame_number": 100,
      "brightness": 0.5,
      "contrast": 0.8,
      "foreground_ratio": 0.15,
      "target_count": 2
    }
  ]
}
```

## Error Handling Strategy

1. **Import Errors**: Wrapped in try-catch during initialization
2. **Logger Initialization**: Graceful degradation if log dir can't be created
3. **API Errors**: All endpoints return proper HTTP status codes
4. **Shutdown Errors**: Cleanup handler catches exceptions and logs them

## Performance Considerations

1. **Logging Overhead**: Minimal - data stored in memory, saved periodically
2. **API Response Time**: <100ms for most queries
3. **Dashboard Refresh**: Every 5 seconds (configurable)
4. **Memory Usage**: ~50-100MB for 1 hour of logging at 30 FPS

