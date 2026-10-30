# Releasing the ACD webapp

```shell
git clone https://github.com/clld/acd
git clone --branch v1.2 --depth 1 https://github.com/lexibank/acd acd-cldf
git clone --branch v5.3 --depth 1 https://github.com/glottolog/glottolog
cd acd
pip install -e .[test]
```

Recreate the database:
```shell
clld initdb development.ini --cldf ../acd-cldf/cldf/cldf-metadata.json --glottolog ../glottolog
```

```shell
pytest
```

Store the tested requirements:
```shell
pip freeze > requirements.txt
```

Store a db dump:
```shell
pg_dump -xO --compress gzip:9 acd > acd.sql.gz
```
