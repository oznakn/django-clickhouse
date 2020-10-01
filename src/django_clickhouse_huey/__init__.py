from django.db.models.signals import post_migrate
from django.dispatch import receiver

from infi.clickhouse_orm import *

from .service import clickhouse
from .model import *


@receiver(post_migrate)
def clickhouse_migrate(sender, **kwargs):
    app_name = kwargs['app_config'].name

    clickhouse.migrate_app(app_name)
