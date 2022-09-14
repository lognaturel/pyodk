import logging
from dataclasses import dataclass, fields
from datetime import datetime
from typing import Dict, List, Optional

from pyodk import validators
from pyodk.endpoints.utils import error_if_not_200
from pyodk.errors import PyODKError
from pyodk.session import ClientSession
from pyodk.utils import STRPTIME_FMT_UTC

log = logging.getLogger(__name__)


@dataclass
class Project:

    id: int
    name: str
    description: str
    keyId: int
    archived: bool
    createdAt: datetime
    appUsers: Optional[int] = None
    forms: Optional[int] = None
    lastSubmission: Optional[str] = None
    updatedAt: Optional[datetime] = None
    deletedAt: Optional[datetime] = None

    def __post_init__(self):
        # Convert date strings to datetime objects.
        dt_fields = ["createdAt", "updatedAt", "deletedAt"]
        for d in dt_fields:
            dt_value = getattr(self, d)
            if isinstance(dt_value, str):
                setattr(self, d, datetime.strptime(dt_value, STRPTIME_FMT_UTC))


class ProjectService:
    def __init__(self, session: ClientSession, default_project_id: Optional[int] = None):
        self.session: ClientSession = session
        self.default_project_id: Optional[int] = default_project_id

    def _read_all_request(self) -> List[Dict]:
        response = self.session.s.get(
            url=f"{self.session.base_url}/v1/projects",
        )
        return error_if_not_200(response=response, log=log, action="project listing")

    def read_all(self) -> List[Project]:
        """
        Read the details of all projects.
        """
        raw = self._read_all_request()
        return [
            Project(**{f.name: r.get(f.name) for f in fields(Project)})
            for r in raw
        ]

    def _read_request(self, project_id: int) -> Dict:
        response = self.session.s.get(
            url=f"{self.session.base_url}/v1/projects/{project_id}",
        )
        return error_if_not_200(response=response, log=log, action="project read")

    def read(self, project_id: Optional[int] = None) -> Project:
        """
        Read the details of a Project.

        :param project_id: The id of the project to read.
        """
        try:
            pid = validators.validate_project_id(
                project_id=project_id, default_project_id=self.default_project_id
            )
        except PyODKError as err:
            log.error(err, exc_info=True)
            raise err
        else:
            raw = self._read_request(project_id=pid)
            return Project(
                **{f.name: raw.get(f.name) for f in fields(Project)}
            )
