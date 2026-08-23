from adapters.resident_adapter import ResidentAdapter
from adapters.benefits_adapter import BenefitsAdapter
from services.identity_matcher import IdentityMatcher


class UnifiedResidentService:
    """
    Combines the Resident Index and Benefits Register.

    Handles:
        - Source failures
        - Partial availability
        - Resident lookup
        - Identity matching
    """

    def __init__(
        self,
        resident_adapter=None,
        benefits_adapter=None,
        identity_matcher=None
    ):

        self.resident_adapter = (
            resident_adapter
            or ResidentAdapter()
        )

        self.benefits_adapter = (
            benefits_adapter
            or BenefitsAdapter()
        )

        self.identity_matcher = (
            identity_matcher
            or IdentityMatcher()
        )

    # ========================================================
    # Get all unified source data
    # ========================================================

    def get_unified_data(self):

        result = {
            "resident_index": {
                "status": "unknown",
                "count": 0,
                "data": []
            },

            "benefits_register": {
                "status": "unknown",
                "count": 0,
                "data": []
            }
        }

        # ----------------------------------------------------
        # Resident Index
        # ----------------------------------------------------

        try:

            residents = (
                self.resident_adapter
                .get_all_residents()
            )

            result["resident_index"] = {
                "status": "success",
                "count": len(residents),
                "data": residents
            }

        except Exception as error:

            result["resident_index"] = {
                "status": "unavailable",
                "count": 0,
                "data": [],
                "reason": str(error)
            }

        # ----------------------------------------------------
        # Benefits Register
        # ----------------------------------------------------

        try:

            benefits = (
                self.benefits_adapter
                .get_records()
            )

            result["benefits_register"] = {
                "status": "success",
                "count": len(benefits),
                "data": benefits
            }

        except Exception as error:

            result["benefits_register"] = {
                "status": "unavailable",
                "count": 0,
                "data": [],
                "reason": str(error)
            }

        return result

    # ========================================================
    # Get unified view for one resident
    # ========================================================

    def get_resident_view(self, resident_id):

        result = {

            "resident_id": resident_id,

            "resident": None,

            "benefits": {
                "status": "not_matched",
                "data": None
            },

            "sources": {

                "resident_index": {
                    "status": "unknown"
                },

                "benefits_register": {
                    "status": "unknown"
                }
            }
        }

        # ----------------------------------------------------
        # Get resident
        # ----------------------------------------------------

        try:

            resident = (
                self.resident_adapter
                .get_resident_by_id(
                    resident_id
                )
            )

            if resident is None:

                result["sources"][
                    "resident_index"
                ] = {
                    "status": "not_found"
                }

            else:

                result["resident"] = resident

                result["sources"][
                    "resident_index"
                ] = {
                    "status": "success"
                }

        except Exception as error:

            result["sources"][
                "resident_index"
            ] = {
                "status": "unavailable",
                "reason": str(error)
            }

        # ----------------------------------------------------
        # If resident doesn't exist, we still check whether
        # Benefits Register is available.
        # ----------------------------------------------------

        try:

            benefits = (
                self.benefits_adapter
                .get_records()
            )

            result["sources"][
                "benefits_register"
            ] = {
                "status": "success"
            }

        except Exception as error:

            result["sources"][
                "benefits_register"
            ] = {
                "status": "unavailable",
                "reason": str(error)
            }

            result["benefits"] = {
                "status": "unavailable",
                "data": None
            }

            return result

        # ----------------------------------------------------
        # If resident wasn't found, don't perform matching.
        # ----------------------------------------------------

        if result["resident"] is None:

            result["benefits"] = {
                "status": "not_matched",
                "confidence": "none",
                "data": None
            }

            return result

        # ----------------------------------------------------
        # Perform identity matching
        # ----------------------------------------------------

        match_result = (
            self.identity_matcher.match(
                result["resident"],
                benefits
            )
        )

        result["benefits"] = match_result

        return result