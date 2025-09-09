import logging
from typing import Optional, Dict, Any, Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from .events import SchedulerEventListener


logger = logging.getLogger(__name__)


class SchedulerManager:
    """调度器管理器"""
    
    def __init__(self, timezone: str = 'Asia/Shanghai'):
        self.scheduler = AsyncIOScheduler(
            timezone=timezone,
            job_defaults={
                'coalesce': True,
                'max_instances': 1,
                'misfire_grace_time': 30
            }
        )
        self.is_running = False
        self.event_listener = SchedulerEventListener()
        self._setup_event_listeners()
    
    def _setup_event_listeners(self):
        """设置事件监听器"""
        self.scheduler.add_listener(
            self.event_listener.job_listener, 
            EVENT_JOB_EXECUTED | EVENT_JOB_ERROR
        )
    
    async def start(self):
        """启动调度器"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("🚀 调度器已启动")
    
    async def shutdown(self, wait: bool = True, timeout: float = 30.0):
        """优雅关闭调度器"""
        if self.is_running:
            logger.info("🔄 正在关闭调度器...")
            try:
                self.scheduler.shutdown(wait=wait)
                self.is_running = False
                logger.info("✅ 调度器已关闭")
            except Exception as e:
                logger.error(f"❌ 关闭调度器时出错: {e}")
    
    def add_interval_job(self, 
                        func: Callable, 
                        seconds: int, 
                        job_id: str,
                        args: tuple = (),
                        kwargs: dict = None,
                        start_immediately: bool = True):
        """添加间隔任务"""
        try:
            self.scheduler.add_job(
                func=func,
                trigger=IntervalTrigger(seconds=seconds),
                id=job_id,
                args=args,
                kwargs=kwargs or {},
                replace_existing=True
            )
            
            if start_immediately:
                self.scheduler.add_job(
                    func=func,
                    trigger='date',
                    id=f"{job_id}_immediate",
                    args=args,
                    kwargs=kwargs or {},
                    replace_existing=True
                )
            
            logger.info(f"✅ 间隔任务已添加: {job_id} (每 {seconds} 秒)")
            
        except Exception as e:
            logger.error(f"❌ 添加任务失败: {e}")
    
    def add_cron_job(self, 
                     func: Callable, 
                     cron_expression: str, 
                     job_id: str,
                     args: tuple = (),
                     kwargs: dict = None):
        """添加 Cron 任务"""
        try:
            parts = cron_expression.split()
            if len(parts) == 5:
                minute, hour, day, month, day_of_week = parts
                self.scheduler.add_job(
                    func=func,
                    trigger=CronTrigger(
                        minute=minute,
                        hour=hour,
                        day=day,
                        month=month,
                        day_of_week=day_of_week
                    ),
                    id=job_id,
                    args=args,
                    kwargs=kwargs or {},
                    replace_existing=True
                )
                logger.info(f"✅ Cron任务已添加: {job_id} ({cron_expression})")
            else:
                raise ValueError("Cron表达式格式错误，应为: 分 时 日 月 周")
                
        except Exception as e:
            logger.error(f"❌ 添加Cron任务失败: {e}")
    
    def remove_job(self, job_id: str):
        """移除任务"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"✅ 任务已移除: {job_id}")
        except Exception as e:
            logger.error(f"❌ 移除任务失败: {e}")
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                return {
                    "id": job.id,
                    "name": job.name,
                    "next_run_time": str(job.next_run_time) if job.next_run_time else None,
                    "trigger": str(job.trigger),
                    "func": f"{job.func.__module__}.{job.func.__name__}"
                }
        except Exception as e:
            logger.error(f"❌ 获取任务状态失败: {e}")
        return None
    
    def list_jobs(self) -> list:
        """列出所有任务"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": str(job.next_run_time) if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        return jobs
