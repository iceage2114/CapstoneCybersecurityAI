from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

class ParameterLocation(str, Enum):
    BODY = "body"
    QUERY = "query"
    PATH = "path"
    HEADER = "header"

@dataclass
class Parameter:
    name: str
    type: str = 'str'
    required: bool = False
    location: ParameterLocation = ParameterLocation.QUERY
    default: Optional[Any] = None
    sub_parameters: Optional[List['Parameter']] = field(default_factory=list)

@dataclass
class Endpoint:
    path: str
    method: str = 'GET'
    parameters: List[Parameter] = field(default_factory=list)
    headers: Dict[str, str] = field(default_factory=dict)
    auth_required: bool = False
    description: Optional[str] = None

@dataclass
class Plugin:
    name: str
    description: str
    base_url: str
    endpoints: List[Endpoint]
    is_tool: bool = False

@dataclass
class RequestDetails:
    method: str
    path: str
    parameters: Dict[str, Any]


