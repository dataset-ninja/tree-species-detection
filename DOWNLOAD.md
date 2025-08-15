Dataset **Tree Species Detection** can be downloaded in [Supervisely format](https://developer.supervisely.com/api-references/supervisely-annotation-json-format):

 [Download](https://assets.supervisely.com/remote/eyJsaW5rIjogInMzOi8vc3VwZXJ2aXNlbHktZGF0YXNldHMvMjI5OF9UcmVlIFNwZWNpZXMgRGV0ZWN0aW9uL3RyZWUtc3BlY2llcy1kZXRlY3Rpb24tRGF0YXNldE5pbmphLnRhciIsICJzaWciOiAiaU1RRnFZUlFXNTJ2NmdscXI1RHpNNzh4U2U0YWxQU1RqZnk0MTVRSFI4QT0ifQ==?response-content-disposition=attachment%3B%20filename%3D%22tree-species-detection-DatasetNinja.tar%22)

As an alternative, it can be downloaded with *dataset-tools* package:
``` bash
pip install --upgrade dataset-tools
```

... using following python code:
``` python
import dataset_tools as dtools

dtools.download(dataset='Tree Species Detection', dst_dir='~/dataset-ninja/')
```
Make sure not to overlook the [python code example](https://developer.supervisely.com/getting-started/python-sdk-tutorials/iterate-over-a-local-project) available on the Supervisely Developer Portal. It will give you a clear idea of how to effortlessly work with the downloaded dataset.

The data in original format can be [downloaded here](https://drive.google.com/drive/folders/1ufsXNT5u29oQOZkmldHgxX2TUkepivEq).