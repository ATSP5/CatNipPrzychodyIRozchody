import os
import posixpath
import re
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Union

CellValue = Union[str, float, bool, None]

_MAIN = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_DOC_REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
_PKG_REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"


class XlsxSheetReader:
    def __init__(self, sheet_name: str = "KPiR 2025"):
        self.workbook_path = r"KsiegaPrzychodowIRozchodow2025.xlsx"
        self.sheet_name = sheet_name

    def rows(self) -> List[List[CellValue]]:
        path = self._resolved_path()
        with zipfile.ZipFile(path) as archive:
            targets = self._sheet_targets(archive)
            if self.sheet_name not in targets:
                raise KeyError("Arkusz '%s' nie istnieje — skoroszyt ma: %s" % (self.sheet_name, ", ".join(targets)))
            strings = self._shared_strings(archive)
            root = ET.fromstring(archive.read(targets[self.sheet_name]))
        result: List[List[CellValue]] = []
        for row in root.iter(_MAIN + "row"):
            values: Dict[int, CellValue] = {}
            for cell in row.findall(_MAIN + "c"):
                values[self._column_index(cell.get("r", "A1"))] = self._cell_value(cell, strings)
            width = max(values) + 1 if values else 0
            result.append([values.get(i) for i in range(width)])
        print("Odczytano %d wierszy arkusza '%s' z %s" % (len(result), self.sheet_name, os.path.basename(path)))
        return result

    def _resolved_path(self) -> str:
        candidates = [self.workbook_path,
                      os.path.join(os.path.dirname(os.path.abspath(__file__)), self.workbook_path)]
        for candidate in candidates:
            if os.path.isfile(candidate):
                return candidate
        raise FileNotFoundError("Nie znaleziono skoroszytu: %s" % self.workbook_path)

    def _sheet_targets(self, archive: zipfile.ZipFile) -> Dict[str, str]:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relations = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        by_id = {rel.get("Id"): rel.get("Target", "") for rel in relations.iter(_PKG_REL + "Relationship")}
        targets: Dict[str, str] = {}
        for sheet in workbook.iter(_MAIN + "sheet"):
            target = by_id.get(sheet.get(_DOC_REL + "id"), "")
            path = target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.join("xl", target))
            targets[sheet.get("name", "")] = path
        return targets

    def _shared_strings(self, archive: zipfile.ZipFile) -> List[str]:
        if "xl/sharedStrings.xml" not in archive.namelist():
            return []
        root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
        return ["".join(t.text or "" for t in item.iter(_MAIN + "t")) for item in root.findall(_MAIN + "si")]

    def _cell_value(self, cell: ET.Element, strings: List[str]) -> CellValue:
        kind = cell.get("t", "n")
        if kind == "inlineStr":
            return "".join(t.text or "" for t in cell.iter(_MAIN + "t"))
        raw: Optional[str] = cell.findtext(_MAIN + "v")
        if raw is None or raw == "":
            return None
        if kind == "s":
            return strings[int(raw)]
        if kind == "b":
            return raw == "1"
        if kind in ("str", "e"):
            return raw
        try:
            return float(raw)
        except ValueError:
            return raw

    @staticmethod
    def _column_index(reference: str) -> int:
        letters = re.match(r"[A-Z]+", reference.upper())
        index = 0
        for letter in letters.group(0) if letters else "A":
            index = index * 26 + (ord(letter) - 64)
        return index - 1
