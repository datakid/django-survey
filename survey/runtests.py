import os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'examples.settings'
test_dir = os.path.dirname(__file__)
sys.path.insert(0, test_dir)

from django.test.utils import get_runner
from django.conf import settings

def runtests():
    test_runner = get_runner(settings)
    failures = test_runner(['survey'], verbosity=1, interactive=True)
    sys.exit(failures)

if __name__ == '__main__':
    runtests()

