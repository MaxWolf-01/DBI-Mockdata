### Very small script for a school exercise to avoid using Mockaroo
Might help if you happen to share the joy of going to HTL Spengergasse.

### Usage
```bash
$ pip install -r requirements.txt 
```

```python
# myscript.py
from pathlib import Path
from faker import Faker
from exporter import CSVExporter
from generator import FakeRecordGenerator
import numpy as np  # optional 
import exrex # optional for generating with regex

faker = Faker() # https://github.com/joke2k/faker

class MyFakeGenerator(FakeRecordGenerator):
    def generate_record(self, idx: int | None = None) -> dict:
        return {
            "id": idx,
            "first_name": faker.first_name(),
            "grade": np.random.choice("12345", p=[0.1, 0.2, 0.4, 0.2, 0.1]),
            "class": exrex.getone("[1-5][A-C](HIF|FIT|HKUI|HBGM)"),
        }

f = MyFakeGenerator()
CSVExporter.export(
    records=f.records(n_records=10),
    headers=f.generate_record(0).keys(),
    path=Path("out", "my_file.csv")
)
```

The full example along with the confusing (german) school-exercise description can be found in the `example` folder. Don't expect nice code.