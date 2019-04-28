import sys
sys.path.append('../')

from Slaver.Until.tool import settings
from Slaver.Scheduler import SlaverScheduler


s = SlaverScheduler.from_settings(settings)
s.run()


