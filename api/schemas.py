from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from datetime import datetime
from pydantic import BaseModel


class RunStatsRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    hashtag: str | None = None
    summary: bool = True


class UserStat(BaseModel):
    start_date: str
    end_date: str
    hashtag: Optional[str]
    uid: int
    name: str
    changesets: int
    map_changes: int
    nodes_create: int
    nodes_modify: int
    nodes_delete: int
    ways_create: int
    ways_modify: int
    ways_delete: int
    relations_create: int
    relations_modify: int
    relations_delete: int
    poi_create: int
    poi_modify: int
    countries: Optional[str] = None
    editors: Optional[str] = None
    hashtags: Optional[str] = None


class UsersResponse(BaseModel):
    filters: Dict[str, Any]
    users: List[UserStat]


class SummaryResponse(BaseModel):
    filters: Dict[str, Any]
    summary: Dict[str, Any]


class TimeSeriesPoint(BaseModel):
    start_date: str
    end_date: str
    hashtag: Optional[str]
    timestamp: str
    users: int
    changesets: int
    map_changes: int
    nodes_create: int
    nodes_modify: int
    nodes_delete: int
    ways_create: int
    ways_modify: int
    ways_delete: int
    relations_create: int
    relations_modify: int
    relations_delete: int
    poi_create: int
    poi_modify: int


class TimeSeriesResponse(BaseModel):
    filters: Dict[str, Any]
    timeseries: List[TimeSeriesPoint]
