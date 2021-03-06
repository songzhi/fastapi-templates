from tempfile import NamedTemporaryFile

import orjson
from fastapi.encoders import jsonable_encoder
from invoke import task

from app.app import app


@task
def codegen_ts(c, out_dir='./api'):
    with NamedTemporaryFile(suffix=".json") as fp:
        fp.write(orjson.dumps(jsonable_encoder(app.openapi(), by_alias=False)))
        fp.flush()

        c.run(f'openapi --output {out_dir} --input {fp.name} --useOptions')
        with c.cd(out_dir):
            c.run('git add -A && git commit -m chore(api):codegen && git pull && git push')


@task
def codegen_ts_to_file(c):
    with open('./statics/spec.json', mode='wb') as fp:
        fp.write(orjson.dumps(jsonable_encoder(app.openapi(), by_alias=False)))
