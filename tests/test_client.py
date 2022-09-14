from typing import List, Tuple
from unittest import TestCase, skip

from mock import MagicMock, patch
from requests import Session

from pyodk.client import Client
from tests.resources import CONFIG_DATA

@skip
class TestUsage(TestCase):
    def test_usage(self):
        with Client() as client:
            projects = client.projects.read_all()
            forms = client.forms.read_all()
            submissions = client.submissions.read_all(form_id=forms[3].xmlFormId)
            form_data = client.submissions.read_all_table(form_id=forms[3].xmlFormId)
            form_data_params = client.submissions.read_all_table(
                form_id="range",
                table_name="Submissions",
                count=True,
            )
            form_odata_metadata = client.forms.read_odata_metadata(form_id="range")
            print(
                [
                    projects,
                    forms,
                    submissions,
                    form_data,
                    form_data_params,
                    form_odata_metadata,
                ]
            )

class TestRequests(TestCase):
    def setUp(self) -> None:
        self.cases: List[Tuple[str,str]] = [
            ("/users", "https://example.com/v1/users"),
            ("users", "https://example.com/v1/users"),
            ("/projects/17/forms", "https://example.com/v1/projects/17/forms"),
            ("projects/17/forms", "https://example.com/v1/projects/17/forms")
        ]

    @patch("pyodk.client.Client._login", MagicMock())
    @patch("pyodk.config.read_config", MagicMock(return_value=CONFIG_DATA))
    def get__builds_path_from_url(self):
        with patch.object(Session, "get") as mock_session:
            for input, output in self.cases:
                with self.subTest(f"client.get({input})"):
                    with Client() as client:
                        response = client.get(input)
                    mock_session.assert_called_with(url=output)

    @patch("pyodk.client.Client._login", MagicMock())
    @patch("pyodk.config.read_config", MagicMock(return_value=CONFIG_DATA))
    def get__passes_on_additional_arguments(self):
        with patch.object(Session, "get") as mock_session:
            with Client() as client:
                response = client.get("/users", params="foo")
            mock_session.assert_called_with(url="https://example.com/v1/projects/1/users", params="foo")