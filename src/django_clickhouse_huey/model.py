from infi.clickhouse_orm import Model as BaseModel, UUIDField, Memory

from .service import clickhouse


class Model(BaseModel):
    id = UUIDField()

    engine = Memory()

    @classmethod
    def objects(cls):
        objects = cls.objects_in(clickhouse.get_db())
        objects.create = clickhouse.create
