"""Frappe DocField type aliases (vendored from frappe/types/DF.py).

`DF.Literal[...]` is used by every Select field in the auto-generated DocType
type blocks. In a .pyi stub a bare `from typing import Literal` is treated as a
private import (PEP 484 strict re-export), so `DF.Literal` would not resolve —
hence the explicit `as Literal` re-export. Regenerate from frappe/types/DF.py
if the framework changes its field types.
"""

from datetime import date, datetime, time
from typing import Literal as Literal

# DocField types
Data = str
Text = str
Autocomplete = Data
Attach = Data
AttachImage = Data
Barcode = Data
Check = bool | int
Code = Text
Color = str
Currency = float
Date = str | date
Datetime = str | datetime
Duration = int
DynamicLink = Data
Float = float
HTMLEditor = Text
Int = int
JSON = Text
Link = Data
LongText = Text
MarkdownEditor = Text
Password = Data
Percent = float
Phone = Data
ReadOnly = Data
Rating = float
Select = Literal
SmallText = Text
TextEditor = Text
Time = str | time
Table = list
TableMultiSelect = list
