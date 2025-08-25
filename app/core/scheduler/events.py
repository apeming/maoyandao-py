"""事件监听器"""
import logging
from apscheduler.events import JobExecutionEvent

logger = logging.getLogger(__name__)

class SchedulerEventListener:
    """调度器事件监听器"""
    
    def job_listener(self, event: JobExecutionEvent):
        """任务执行事件监听器"""
        if event.exception:
            logger.error(f"❌ 任务 {event.job_id} 执行失败: {event.exception}")
            # 这里可以添加告警通知逻辑
            self._send_alert(event.job_id, str(event.exception))
        else:
            logger.info(f"✅ 任务 {event.job_id} 执行成功")
    
    def _send_alert(self, job_id: str, error_message: str):
        """发送告警通知（可选实现）"""
        # 可以集成钉钉、企业微信、邮件等通知方式
        pass
