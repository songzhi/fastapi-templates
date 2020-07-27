import click
import pytest
import uvicorn


@click.group()
def cli():
    ...


@cli.command()
def runserver():
    import os
    os.environ['DEV'] = 'fastapi'
    uvicorn.run('app.app:app', debug=True, reload=True, ssl_keyfile='statics/localhost+2-key.pem',
                ssl_certfile='statics/localhost+2.pem', ssl_cert_reqs=False)


@cli.command()
def test():
    import os

    os.environ['TEST'] = 'pytest'
    pytest.main(['-x', 'tests'])


if __name__ == '__main__':
    cli()
