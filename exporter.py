import csv
from pathlib import Path
from typing import Protocol, Iterator, TypeVar, Collection

T = TypeVar('T')


class Exporter(Protocol):
    @staticmethod
    def export(records: Iterator[T], path: Path) -> None:
        ...


class CSVExporter:
    @staticmethod
    def export(records: Iterator[dict], path: Path, headers: Collection[str]) -> None:
        with path.open('w') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for record in records:
                writer.writerow(record)
