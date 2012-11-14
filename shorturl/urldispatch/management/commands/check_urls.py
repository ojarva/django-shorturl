from django.core.management.base import BaseCommand, CommandError
from urldispatch.models import Url
from optparse import make_option


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
     make_option('--verbose',
      action='store_true',
      dest='verbose',
      default=False,
      help='Print status messages'),
    )
    args = ''
    help = 'Checks whether URLs are working'

    def handle(self, *args, **options):
        for url in Url.objects.filter(active=True):
            data = url.test_url()
            if options.get("verbose", False):
                self.stdout.write("%s:" % url.get_short_url())
                for _key in data:
                    self.stdout.write(" %s=%s" % (_key, data[_key]))
                self.stdout.write("\n")
