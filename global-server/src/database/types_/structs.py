import typing as _t
from datetime import datetime as _dt


class TaskTimeLimitations(_t.TypedDict):
    start_execution: _t.NotRequired[_dt]
    complete_before: _t.NotRequired[_dt]
    fail_on_late_start: _t.NotRequired[_dt]
    fail_on_late_complete: _t.NotRequired[_dt]
