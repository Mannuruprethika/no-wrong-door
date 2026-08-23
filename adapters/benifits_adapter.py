import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import xml.etree.ElementTree as ET


class BenefitsAdapter:
    """
    Adapter for the Benefits Register XML service.

    The service can be slow and can occasionally return HTTP 500.
    This adapter handles retries and converts XML into Python data.
    """

    def __init__(
        self,
        base_url="http://127.0.0.1:8082",
        timeout=3,
        max_retries=3
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

    def _request_xml(self):
        """
        Make a request to the Benefits Register.

        Returns:
            XML text if successful.

        Raises:
            Exception if all attempts fail.
        """

        url = f"{self.base_url}/records"

        last_error = None

        for attempt in range(1, self.max_retries + 1):

            try:

                request = Request(
                    url,
                    method="GET",
                    headers={
                        "Accept": "application/xml"
                    }
                )

                with urlopen(
                    request,
                    timeout=self.timeout
                ) as response:

                    return response.read().decode("utf-8")

            except (HTTPError, URLError, TimeoutError) as error:

                last_error = error

                print(
                    f"Benefits Register attempt "
                    f"{attempt}/{self.max_retries} failed: {error}"
                )

                if attempt < self.max_retries:

                    # Small exponential backoff.
                    delay = 0.2 * (2 ** (attempt - 1))

                    time.sleep(delay)

        raise RuntimeError(
            f"Benefits Register unavailable after "
            f"{self.max_retries} attempts: {last_error}"
        )

    def get_records(self):
        """
        Retrieve and parse all Benefits Register records.

        Returns:
            List of dictionaries.
        """

        xml_text = self._request_xml()

        root = ET.fromstring(xml_text)

        records = []

        for record in root.findall("Record"):

            records.append(
                {
                    "reference": self._get_text(
                        record,
                        "Ref"
                    ),
                    "name": self._get_text(
                        record,
                        "Name"
                    ),
                    "date_of_birth": self._get_text(
                        record,
                        "Born"
                    ),
                    "address": self._get_text(
                        record,
                        "Addr"
                    ),
                    "town": self._get_text(
                        record,
                        "Town"
                    ),
                    "benefit_code": self._get_text(
                        record,
                        "BenefitCode"
                    ),
                    "review_due": self._get_text(
                        record,
                        "ReviewDue"
                    )
                }
            )

        return records

    @staticmethod
    def _get_text(parent, tag):
        """
        Safely retrieve text from an XML element.
        """

        element = parent.find(tag)

        if element is None:
            return None

        return element.text
