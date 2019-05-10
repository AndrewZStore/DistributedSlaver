import sys
sys.path.append('../')

from Slaver.Until.tool import settings
from Slaver.Scheduler import SlaverScheduler

def run():
    s = SlaverScheduler.from_settings(settings)
    s.run()


if __name__ == '__main__':
    run()

