"""
Health monitoring service for external dependencies
Monitors Redis, Qdrant, and other services and logs when they come online
"""

import asyncio
import logging
from typing import Dict, Optional, Callable
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

class HealthMonitor:
    """Monitor health of external services and log when they come online"""
    
    def __init__(self):
        self.services: Dict[str, Dict] = {}
        self.check_interval = 30  # seconds
        self.running = False
        self._task: Optional[asyncio.Task] = None
        
    def register_service(
        self, 
        name: str, 
        check_function: Callable[[], bool], 
        on_available: Optional[Callable] = None,
        on_unavailable: Optional[Callable] = None
    ):
        """Register a service for health monitoring"""
        self.services[name] = {
            'check_function': check_function,
            'on_available': on_available,
            'on_unavailable': on_unavailable,
            'last_status': None,
            'last_check': None,
            'consecutive_failures': 0,
            'total_downtime': timedelta(),
            'last_failure_time': None
        }
        logger.info(f"🔍 Registered health monitoring for {name}")
    
    async def start_monitoring(self):
        """Start the health monitoring loop"""
        if self.running:
            return
            
        self.running = True
        logger.info("🏥 Starting health monitoring service...")
        
        # Initial check
        await self._check_all_services()
        
        # Start monitoring loop
        self._task = asyncio.create_task(self._monitoring_loop())
    
    async def stop_monitoring(self):
        """Stop the health monitoring"""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("🏥 Health monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                await asyncio.sleep(self.check_interval)
                await self._check_all_services()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Health monitoring error: {e}")
    
    async def _check_all_services(self):
        """Check health of all registered services"""
        for service_name in self.services:
            await self._check_service(service_name)
    
    async def _check_service(self, service_name: str):
        """Check health of a specific service"""
        service = self.services[service_name]
        current_time = datetime.now()
        
        try:
            # Run the health check
            is_healthy = await asyncio.get_event_loop().run_in_executor(
                None, service['check_function']
            )
            
            previous_status = service['last_status']
            service['last_status'] = is_healthy
            service['last_check'] = current_time
            
            if is_healthy:
                # Service is healthy
                if previous_status is False:
                    # Service just came back online
                    downtime = self._calculate_downtime(service, current_time)
                    logger.info(f"🟢 {service_name} is now ONLINE! (was down for {downtime})")
                    
                    # Call the on_available callback
                    if service['on_available']:
                        try:
                            await asyncio.get_event_loop().run_in_executor(
                                None, service['on_available']
                            )
                        except Exception as e:
                            logger.error(f"❌ Error in {service_name} on_available callback: {e}")
                
                # Reset failure counters
                service['consecutive_failures'] = 0
                service['last_failure_time'] = None
                
            else:
                # Service is unhealthy
                service['consecutive_failures'] += 1
                
                if previous_status is True:
                    # Service just went offline
                    logger.warning(f"🔴 {service_name} is now OFFLINE")
                    service['last_failure_time'] = current_time
                    
                    # Call the on_unavailable callback
                    if service['on_unavailable']:
                        try:
                            await asyncio.get_event_loop().run_in_executor(
                                None, service['on_unavailable']
                            )
                        except Exception as e:
                            logger.error(f"❌ Error in {service_name} on_unavailable callback: {e}")
                
                elif service['consecutive_failures'] % 10 == 0:  # Log every 10th failure
                    downtime = self._calculate_downtime(service, current_time)
                    logger.warning(f"🔴 {service_name} still offline (down for {downtime}, {service['consecutive_failures']} consecutive failures)")
        
        except Exception as e:
            logger.error(f"❌ Error checking {service_name} health: {e}")
            service['last_status'] = False
            service['consecutive_failures'] += 1
    
    def _calculate_downtime(self, service: Dict, current_time: datetime) -> str:
        """Calculate how long a service has been down"""
        if service['last_failure_time']:
            downtime = current_time - service['last_failure_time']
            total_seconds = int(downtime.total_seconds())
            
            if total_seconds < 60:
                return f"{total_seconds}s"
            elif total_seconds < 3600:
                return f"{total_seconds // 60}m {total_seconds % 60}s"
            else:
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                return f"{hours}h {minutes}m"
        return "unknown"
    
    def get_service_status(self, service_name: str) -> Optional[bool]:
        """Get the current status of a service"""
        if service_name in self.services:
            return self.services[service_name]['last_status']
        return None
    
    def get_all_statuses(self) -> Dict[str, Dict]:
        """Get status of all monitored services"""
        statuses = {}
        for name, service in self.services.items():
            statuses[name] = {
                'status': service['last_status'],
                'last_check': service['last_check'],
                'consecutive_failures': service['consecutive_failures']
            }
        return statuses

# Global health monitor instance
health_monitor = HealthMonitor()
