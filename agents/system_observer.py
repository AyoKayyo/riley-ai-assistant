"""
System Observer Agent (Riley's Senses)
Monitors hardware stats (CPU, RAM, Disk, Network) to give the Companion "physical awareness"
"""
import psutil
import datetime
import platform

class SystemObserver:
    """
    Provides real-time system health data.
    Acts as the 'nervous system' for the Companion.
    """
    
    def __init__(self):
        self.os_info = f"{platform.system()} {platform.release()}"
        self.processor = platform.processor()
    
    def get_system_status(self):
        """Get comprehensive system health snapshot"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        battery = psutil.sensors_battery()
        
        # Determine status level
        status = "HEALTHY"
        if cpu_percent > 85 or memory.percent > 90:
            status = "STRESSED"
        
        # Battery context
        power_status = "Plugged In"
        if battery:
            power_status = f"{battery.percent}% ({'Plugged In' if battery.power_plugged else 'Battery'})"
        
        return {
            "status": status,
            "cpu": {
                "usage": cpu_percent,
                "count": psutil.cpu_count()
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 1),
                "used_percent": memory.percent,
                "available_gb": round(memory.available / (1024**3), 1)
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 1),
                "free_gb": round(disk.free / (1024**3), 1),
                "percent": disk.percent
            },
            "power": power_status,
            "os": self.os_info,
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def get_formatted_report(self):
        """Return a natural language report for the LLM"""
        stats = self.get_system_status()
        
        report = f"""SYSTEM SENSES REPORT:
- Heartbeat (CPU): {stats['cpu']['usage']}% usage
- Brain Space (RAM): {stats['memory']['used_percent']}% used ({stats['memory']['available_gb']}GB free)
- Storage (Disk): {stats['disk']['percent']}% full ({stats['disk']['free_gb']}GB free)
- Energy: {stats['power']}
- Status: {stats['status']}"""

        # Add urgent warnings
        if stats['status'] == "STRESSED":
            report += "\n⚠️ SYSTEM IS UNDER HEAVY LOAD. I feel stressed."
            
        return report

# Standalone check
if __name__ == "__main__":
    observer = SystemObserver()
    print(observer.get_formatted_report())
