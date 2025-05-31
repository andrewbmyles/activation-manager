"""
Performance monitoring for search operations
Ensures we maintain <100ms latency and 98% filtering effectiveness
"""
import time
import logging
from functools import wraps
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Track performance metrics for search operations"""
    operation: str
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    result_count: Optional[int] = None
    filtered_count: Optional[int] = None
    filter_reduction: Optional[float] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def complete(self, result_count: int = None, filtered_count: int = None):
        """Mark operation as complete and calculate metrics"""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        self.result_count = result_count
        self.filtered_count = filtered_count
        
        if result_count and filtered_count and result_count > filtered_count:
            self.filter_reduction = 1 - (filtered_count / result_count)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            'operation': self.operation,
            'duration_ms': round(self.duration_ms, 2) if self.duration_ms else None,
            'result_count': self.result_count,
            'filtered_count': self.filtered_count,
            'filter_reduction': round(self.filter_reduction, 3) if self.filter_reduction else None,
            'error': self.error,
            'timestamp': datetime.fromtimestamp(self.start_time).isoformat(),
            'metadata': self.metadata
        }


class PerformanceMonitor:
    """Monitor and track search performance against baselines"""
    
    # Performance baselines (must maintain these)
    BASELINES = {
        'search_latency_ms': 100.0,      # Max 100ms search latency
        'filter_reduction': 0.95,         # Min 95% reduction in duplicates
        'error_rate': 0.01,               # Max 1% error rate
        'memory_usage_mb': 512,           # Max 512MB memory
    }
    
    def __init__(self):
        self.metrics_history = []
        self.error_count = 0
        self.total_requests = 0
        
    def monitor_operation(self, operation: str):
        """Decorator to monitor an operation's performance"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                metrics = PerformanceMetrics(operation=operation)
                
                # Add query info to metadata
                if args and hasattr(args[0], '__dict__'):
                    if 'query' in kwargs:
                        metrics.metadata['query'] = kwargs['query'][:50]  # First 50 chars
                
                try:
                    # Execute operation
                    result = func(*args, **kwargs)
                    
                    # Extract metrics from result
                    if isinstance(result, dict):
                        metrics.complete(
                            result_count=result.get('total_found'),
                            filtered_count=len(result.get('results', []))
                        )
                    
                    # Check performance against baselines
                    self._check_performance(metrics)
                    
                    return result
                    
                except Exception as e:
                    metrics.error = str(e)
                    metrics.complete()
                    self.error_count += 1
                    logger.error(f"{operation} failed: {e}, duration: {metrics.duration_ms:.2f}ms")
                    raise
                    
                finally:
                    self.total_requests += 1
                    self.metrics_history.append(metrics)
                    
                    # Keep only last 1000 metrics
                    if len(self.metrics_history) > 1000:
                        self.metrics_history = self.metrics_history[-1000:]
                        
            return wrapper
        return decorator
    
    def _check_performance(self, metrics: PerformanceMetrics):
        """Check if performance meets baselines and log warnings"""
        if metrics.duration_ms and metrics.duration_ms > self.BASELINES['search_latency_ms']:
            logger.warning(
                f"⚠️ Performance degradation: {metrics.operation} took {metrics.duration_ms:.2f}ms "
                f"(baseline: {self.BASELINES['search_latency_ms']}ms)"
            )
        
        if metrics.filter_reduction and metrics.filter_reduction < self.BASELINES['filter_reduction']:
            logger.warning(
                f"⚠️ Filtering degradation: {metrics.operation} reduced by {metrics.filter_reduction:.1%} "
                f"(baseline: {self.BASELINES['filter_reduction']:.1%})"
            )
        
        # Log successful operations that are close to baseline
        if metrics.duration_ms and 80 < metrics.duration_ms < 100:
            logger.info(f"📊 {metrics.operation}: {metrics.duration_ms:.2f}ms (approaching limit)")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = self.metrics_history[-100:]  # Last 100 operations
        
        # Calculate statistics
        durations = [m.duration_ms for m in recent_metrics if m.duration_ms]
        reductions = [m.filter_reduction for m in recent_metrics if m.filter_reduction]
        
        stats = {
            'total_requests': self.total_requests,
            'error_rate': self.error_count / self.total_requests if self.total_requests > 0 else 0,
            'avg_latency_ms': sum(durations) / len(durations) if durations else 0,
            'max_latency_ms': max(durations) if durations else 0,
            'min_latency_ms': min(durations) if durations else 0,
            'avg_filter_reduction': sum(reductions) / len(reductions) if reductions else 0,
            'baseline_violations': {
                'latency': sum(1 for d in durations if d > self.BASELINES['search_latency_ms']),
                'filtering': sum(1 for r in reductions if r < self.BASELINES['filter_reduction'])
            }
        }
        
        return stats
    
    def log_statistics(self):
        """Log current performance statistics"""
        stats = self.get_statistics()
        if stats:
            logger.info(f"📊 Performance Stats: {json.dumps(stats, indent=2)}")
            
            # Alert if consistently failing baselines
            if stats['baseline_violations']['latency'] > 10:
                logger.error("❌ Consistent latency violations detected!")
            if stats['baseline_violations']['filtering'] > 5:
                logger.error("❌ Consistent filtering violations detected!")


# Global monitor instance
_monitor = PerformanceMonitor()


def monitor_performance(operation: str):
    """Decorator to monitor performance of an operation"""
    return _monitor.monitor_operation(operation)


def get_performance_stats() -> Dict[str, Any]:
    """Get current performance statistics"""
    return _monitor.get_statistics()


def log_performance_stats():
    """Log current performance statistics"""
    _monitor.log_statistics()