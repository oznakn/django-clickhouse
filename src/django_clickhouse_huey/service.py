import datetime
import uuid

from importlib.util import find_spec

from django.conf import settings
from django.core.cache import caches

from infi.clickhouse_orm import Model as BaseModel, Database, StringField, DateField, MergeTree, ServerError, \
    DatabaseException, import_submodules

clickhouse_cache = caches['clickhouse']


class MigrationHistory(BaseModel):
    package_name = StringField()
    module_name = StringField()
    applied = DateField()

    engine = MergeTree('applied', ('package_name', 'module_name'))

    @classmethod
    def table_name(cls):
        return 'django_clickhouse_migrations'


class ClickHouseService:
    def __init__(self, params):
        name = params.CLICKHOUSE['NAME']

        options = params.CLICKHOUSE['OPTIONS']

        self._created_tables = set()
        self._db = Database(name, **options)

    def get_db(self):
        return self._db

    def create(self, value):
        type_name = type(value).__name__

        if type_name not in self._created_tables:
            self._db.create_table(type(value))
            self._created_tables.add(type_name)

        value.id = uuid.uuid4()
        self._db.insert([value])

        return value.id

    def delete(self, value):
        type(value).objects_in(self._db).filter(id=value.id).delete()

    def set_migration_applied(self, migrations_package, name):
        migration_history = MigrationHistory(package_name=migrations_package, module_name=name,
                                             applied=datetime.date.today())

        self._db.insert([migration_history])

    def get_applied_migrations(self, migrations_package):
        qs = MigrationHistory.objects_in(self._db).filter(package_name=migrations_package).only('module_name')

        try:
            return set(obj.module_name for obj in qs)
        except ServerError as ex:
            # Database doesn't exist or table doesn't exist
            # I added string check, when code parsing broke in infi.clickouse_orm
            # See https://github.com/Infinidat/infi.clickhouse_orm/issues/108
            if ex.code in {81, 60} or 'Code: 60' in ex.message or 'Code: 81,' in ex.message:
                return set()
            raise ex
        except DatabaseException as ex:
            # If database doesn't exist no migrations are applied
            # This prevents readonly=True + db_exists=False infi exception
            if str(ex) == 'Database does not exist, and cannot be created under readonly connection':
                return set()
            raise ex

    def migrate_app(self, app_label) -> None:
        migrations_package = "%s.%s" % (app_label, 'clickhouse_migrations')

        if find_spec(migrations_package) is not None:
            applied_migrations = self.get_applied_migrations(migrations_package)
            modules = import_submodules(migrations_package)
            unapplied_migrations = set(modules.keys()) - applied_migrations

            for name in sorted(unapplied_migrations):
                print('Applying ClickHouse migration %s for app %s' % (name, app_label))
                migration = modules[name].Migration()
                migration.apply()

                self.set_migration_applied(migrations_package, name)


clickhouse = ClickHouseService(settings)
