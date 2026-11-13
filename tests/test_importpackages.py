import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from importpackages import load_mapping, upload_and_start_import, wait_for_import


class ImportPackagesTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.package = self.directory / "sample.json"
        self.package.write_text('{"name": "sample"}', encoding="utf-8")

    def test_exclude_authorization_preserves_mapping_and_overrides_options(self):
        mapping_file = self.directory / "mapping.json"
        mapping_file.write_text(
            json.dumps({"version": 1, "connectors": {"table": []}, "options": {"keep": True}}),
            encoding="utf-8",
        )

        mapping = load_mapping(str(mapping_file), True)

        self.assertEqual(mapping["connectors"], {"table": []})
        self.assertEqual(mapping["options"], {"promoteAuthorization": False})

    @patch("importpackages.callrestapi")
    def test_upload_and_import_use_transfer_rest_endpoints(self, callrestapi_mock):
        callrestapi_mock.side_effect = [
            {"id": "package-1", "name": "sample"},
            {"id": "job-1", "state": "running"},
        ]
        mapping = {"version": 1, "options": {"promoteAuthorization": False}}

        job = upload_and_start_import(str(self.package), mapping)

        upload_call, import_call = callrestapi_mock.call_args_list
        self.assertEqual(upload_call.args[:2], ("/transfer/packages", "postmultipart"))
        self.assertEqual(upload_call.kwargs["data"]["file"][0], "sample.json")
        self.assertEqual(upload_call.kwargs["data"]["file"][2], "application/json")
        self.assertEqual(import_call.args[:2], ("/transfer/importJobs", "post"))
        self.assertEqual(
            import_call.kwargs["contentType"],
            "application/vnd.sas.transfer.import.request+json",
        )
        self.assertEqual(import_call.kwargs["data"]["packageUri"], "/transfer/packages/package-1")
        self.assertEqual(import_call.kwargs["data"]["mapping"], mapping)
        self.assertEqual(job["id"], "job-1")

    @patch("importpackages.time.sleep")
    @patch("importpackages.callrestapi")
    def test_wait_for_import_polls_until_terminal_state(self, callrestapi_mock, sleep_mock):
        callrestapi_mock.return_value = {"id": "job-1", "state": "completed"}
        running_job = {
            "id": "job-1",
            "state": "running",
            "links": [{"rel": "self", "href": "/transfer/importJobs/job-1"}],
        }

        completed_job = wait_for_import(running_job, poll_interval=0)

        callrestapi_mock.assert_called_once_with("/transfer/importJobs/job-1", "get")
        sleep_mock.assert_called_once_with(0)
        self.assertEqual(completed_job["state"], "completed")


if __name__ == "__main__":
    unittest.main()