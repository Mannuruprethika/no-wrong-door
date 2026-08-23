from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import urlparse

from adapters.resident_adapter import ResidentAdapter
from adapters.benefits_adapter import BenefitsAdapter
from services.unified_service import UnifiedResidentService


# ============================================================
# Create adapters
# ============================================================

resident_adapter = ResidentAdapter()

benefits_adapter = BenefitsAdapter()


# ============================================================
# Create unified service
# ============================================================

unified_service = UnifiedResidentService(
    resident_adapter=resident_adapter,
    benefits_adapter=benefits_adapter
)


# ============================================================
# API Handler
# ============================================================

class UnifiedAPIHandler(BaseHTTPRequestHandler):

    # --------------------------------------------------------
    # Send JSON
    # --------------------------------------------------------

    def send_json(
        self,
        status_code,
        data
    ):

        body = json.dumps(
            data,
            indent=2
        ).encode("utf-8")

        self.send_response(
            status_code
        )

        self.send_header(
            "Content-Type",
            "application/json"
        )

        self.send_header(
            "Content-Length",
            str(len(body))
        )

        self.end_headers()

        self.wfile.write(body)

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    def do_GET(self):

        parsed = urlparse(
            self.path
        )

        path = parsed.path

        # ====================================================
        # GET /health
        # ====================================================

        if path == "/health":

            self.send_json(
                200,
                {
                    "status": "ok",
                    "service": (
                        "No Wrong Door Unified API"
                    )
                }
            )

            return

        # ====================================================
        # GET /residents
        #
        # Full data endpoint.
        # Mainly useful for testing/debugging.
        # ====================================================

        if path == "/residents":

            result = (
                unified_service
                .get_unified_data()
            )

            self.send_json(
                200,
                result
            )

            return

        # ====================================================
        # GET /resident/{id}
        #
        # Example:
        #
        # /resident/R-10394
        # ====================================================

        if path.startswith(
            "/resident/"
        ):

            resident_id = path.split(
                "/resident/",
                1
            )[1]

            if not resident_id:

                self.send_json(
                    400,
                    {
                        "error": (
                            "Resident ID is required"
                        )
                    }
                )

                return

            result = (
                unified_service
                .get_resident_view(
                    resident_id
                )
            )

            # ------------------------------------------------
            # Resident not found
            # ------------------------------------------------

            resident_status = (
                result[
                    "sources"
                ][
                    "resident_index"
                ][
                    "status"
                ]
            )

            if (
                resident_status
                == "not_found"
            ):

                self.send_json(
                    404,
                    result
                )

                return

            # ------------------------------------------------
            # Resident service unavailable
            # ------------------------------------------------

            if (
                resident_status
                == "unavailable"
            ):

                self.send_json(
                    503,
                    result
                )

                return

            # ------------------------------------------------
            # Successful response
            # ------------------------------------------------

            self.send_json(
                200,
                result
            )

            return

        # ====================================================
        # Unknown endpoint
        # ====================================================

        self.send_json(
            404,
            {
                "error": "Endpoint not found",

                "available_endpoints": [
                    "GET /health",
                    "GET /residents",
                    "GET /resident/{id}"
                ]
            }
        )

    # --------------------------------------------------------
    # Console logging
    # --------------------------------------------------------

    def log_message(
        self,
        format,
        *args
    ):

        print(
            f"[API] "
            f"{self.address_string()} - "
            f"{format % args}"
        )


# ============================================================
# Start server
# ============================================================

def main():

    host = "127.0.0.1"

    port = 8000

    server = HTTPServer(
        (host, port),
        UnifiedAPIHandler
    )

    print()

    print(
        "========================================"
    )

    print(
        "No Wrong Door - Unified API"
    )

    print(
        "========================================"
    )

    print()

    print(
        f"Server running on "
        f"http://{host}:{port}"
    )

    print()

    print("Endpoints:")

    print(
        "  GET /health"
    )

    print(
        "  GET /residents"
    )

    print(
        "  GET /resident/{id}"
    )

    print()

    print(
        "Press Ctrl+C to stop."
    )

    print()

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print()
        print(
            "Stopping Unified API..."
        )

    finally:

        server.server_close()


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":

    main()