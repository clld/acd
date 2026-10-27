# Releasing the ACD webapp

```shell
git clone https://github.com/clld/acd
git clone https://github.com/lexibank/acd acd-cldf
cd acd-cldf
git checkout v1.2
cd ../acd
pip install -e .[test]
```

Recreate the database:
```shell
clld initdb development.ini --cldf ../acd-cldf/cldf/cldf-metadata.json --glottolog ../../glottolog/glottolog
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
pg_dump -xO acd > acd.sql
zip acd.sql.zip acd.sql
rm acd.sql
```
