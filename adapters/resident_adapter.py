import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class ResidentAdapter:
    """
    Adapter responsible for communicating with the Resident Index REST service.
    """

    def __init__(
        self,
        base_url="http://127.0.0.1:8081",
        timeout=3
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get_json(self, url):
        """
        Perform a GET request and return the JSON response.
        """

        request = Request(
            url,
            method="GET",
            headers={
                "Accept": "application/json"
            }
        )

        with urlopen(request, timeout=self.timeout) as response:
            body = response.read().decode("utf-8")
            return json.loads(body)

    def get_page(self, page, page_size=25):
        """
        Retrieve one page from the Resident Index.
        """

        url = (
            f"{self.base_url}/residents"
            f"?page={page}&page_size={page_size}"
        )

        return self._get_json(url)

    def get_all_residents(self):
        """
        Retrieve all residents while removing duplicates
        that may appear across pages.
        """

        residents = []
        seen_ids = set()

        page = 1
        page_size = 25

        while True:

            data = self.get_page(
                page=page,
                page_size=page_size
            )

            results = data.get("results", [])

            for resident in results:

                resident_id = resident.get("id")

                # Ignore malformed records without an ID.
                if not resident_id:
                    continue

                # Prevent duplicate records across pages.
                if resident_id in seen_ids:
                    continue

                seen_ids.add(resident_id)
                residents.append(resident)

            if not data.get("has_more", False):
                break

            page += 1
    

        return residents
    def get_resident_by_id(self, resident_id):
        """
        Find a resident by their stable Resident Index ID.
        """

        residents = self.get_all_residents()

        for resident in residents:
            if resident.get("id") == resident_id:
                return resident

        return None
