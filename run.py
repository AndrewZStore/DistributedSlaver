from .Until.tool import settings
from .Scheduler import SlaverScheduler


s = SlaverScheduler.from_settings(settings)
s.run()


