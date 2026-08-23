import re


class IdentityMatcher:
    """
    Matches a Resident Index record against Benefits Register records.

    Matching fields:
        - Name
        - Date of birth
        - Address
        - Town / City

    Address abbreviations are normalized so that values such as
    'Ave' and 'Avenue' are treated as equivalent.
    """

    # ========================================================
    # Address abbreviations
    # ========================================================

    ADDRESS_ABBREVIATIONS = {
        "rd": "road",
        "ave": "avenue",
        "st": "street",
        "dr": "drive",
        "ln": "lane",
        "ct": "court",
        "blvd": "boulevard",
        "hwy": "highway",
        "pl": "place",
        "pkwy": "parkway",
        "ter": "terrace",
        "cir": "circle"
    }

    # ========================================================
    # General text normalization
    # ========================================================

    def normalize_text(self, value):

        if value is None:
            return ""

        value = str(value).strip().lower()

        value = re.sub(
            r"[^a-z0-9\s]",
            " ",
            value
        )

        value = re.sub(
            r"\s+",
            " ",
            value
        )

        return value.strip()

    # ========================================================
    # Name normalization
    # ========================================================

    def normalize_name(self, value):
        """
        Convert:

            QUILL, Paul

        into:

            paul quill
        """

        if not value:
            return ""

        value = str(value).strip()

        if "," in value:

            parts = value.split(
                ",",
                1
            )

            last_name = parts[0].strip()

            first_name = parts[1].strip()

            value = (
                f"{first_name} "
                f"{last_name}"
            )

        return self.normalize_text(value)

    # ========================================================
    # Address normalization
    # ========================================================

    def normalize_address(self, value):
        """
        Normalize common address abbreviations.

        Examples:

            326 Sycamore Ave
            326 Sycamore Avenue

        both become:

            326 sycamore avenue
        """

        value = self.normalize_text(value)

        if not value:
            return ""

        words = value.split()

        normalized_words = []

        for word in words:

            replacement = (
                self.ADDRESS_ABBREVIATIONS
                .get(word, word)
            )

            normalized_words.append(
                replacement
            )

        return " ".join(
            normalized_words
        )

    # ========================================================
    # Name comparison
    # ========================================================

    def names_match(
        self,
        resident,
        benefit
    ):

        resident_name = (
            f"{resident.get('first_name', '')} "
            f"{resident.get('last_name', '')}"
        )

        benefit_name = (
            benefit.get("name")
        )

        return (
            self.normalize_name(
                resident_name
            )
            ==
            self.normalize_name(
                benefit_name
            )
        )

    # ========================================================
    # Date of birth comparison
    # ========================================================

    def date_of_birth_match(
        self,
        resident,
        benefit
    ):

        resident_dob = (
            resident.get("date_of_birth")
        )

        benefit_dob = (
            benefit.get("date_of_birth")
        )

        if not resident_dob or not benefit_dob:
            return False

        return (
            str(resident_dob).strip()
            ==
            str(benefit_dob).strip()
        )

    # ========================================================
    # Address comparison
    # ========================================================

    def address_match(
        self,
        resident,
        benefit
    ):

        resident_address = (
            resident.get("address_line")
        )

        benefit_address = (
            benefit.get("address")
        )

        if (
            not resident_address
            or not benefit_address
        ):
            return False

        return (
            self.normalize_address(
                resident_address
            )
            ==
            self.normalize_address(
                benefit_address
            )
        )

    # ========================================================
    # Town comparison
    # ========================================================

    def town_match(
        self,
        resident,
        benefit
    ):

        resident_city = (
            resident.get("city")
        )

        benefit_town = (
            benefit.get("town")
        )

        if (
            not resident_city
            or not benefit_town
        ):
            return False

        return (
            self.normalize_text(
                resident_city
            )
            ==
            self.normalize_text(
                benefit_town
            )
        )

    # ========================================================
    # Calculate score
    # ========================================================

    def calculate_score(
        self,
        resident,
        benefit
    ):

        score = 0

        matched_fields = []

        # --------------------------------------------
        # Name
        # --------------------------------------------

        if self.names_match(
            resident,
            benefit
        ):

            score += 50

            matched_fields.append(
                "name"
            )

        # --------------------------------------------
        # Date of birth
        # --------------------------------------------

        if self.date_of_birth_match(
            resident,
            benefit
        ):

            score += 30

            matched_fields.append(
                "date_of_birth"
            )

        # --------------------------------------------
        # Address
        # --------------------------------------------

        if self.address_match(
            resident,
            benefit
        ):

            score += 15

            matched_fields.append(
                "address"
            )

        # --------------------------------------------
        # Town
        # --------------------------------------------

        if self.town_match(
            resident,
            benefit
        ):

            score += 5

            matched_fields.append(
                "town"
            )

        return (
            score,
            matched_fields
        )

    # ========================================================
    # Find best match
    # ========================================================

    def match(
        self,
        resident,
        benefits_records
    ):

        candidates = []

        for benefit in benefits_records:

            score, matched_fields = (
                self.calculate_score(
                    resident,
                    benefit
                )
            )

            has_name = (
                "name"
                in matched_fields
            )

            has_dob = (
                "date_of_birth"
                in matched_fields
            )

            has_address = (
                "address"
                in matched_fields
            )

            has_town = (
                "town"
                in matched_fields
            )

            # ----------------------------------------
            # Safe candidate rules
            # ----------------------------------------

            name_and_dob = (
                has_name
                and has_dob
            )

            name_address_town = (
                has_name
                and has_address
                and has_town
            )

            if (
                name_and_dob
                or name_address_town
            ):

                candidates.append(
                    {
                        "record": benefit,
                        "score": score,
                        "matched_fields": (
                            matched_fields
                        )
                    }
                )

        # ====================================================
        # No candidate
        # ====================================================

        if not candidates:

            return {
                "status": "not_matched",
                "confidence": "none",
                "score": 0,
                "matched_fields": [],
                "data": None
            }

        # ====================================================
        # Sort by score
        # ====================================================

        candidates.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        best = candidates[0]

        # ====================================================
        # Check ambiguity
        # ====================================================

        same_score_candidates = [
            candidate
            for candidate in candidates
            if candidate["score"]
            == best["score"]
        ]

        if len(same_score_candidates) > 1:

            return {
                "status": "ambiguous",
                "confidence": "none",
                "score": best["score"],
                "matched_fields": (
                    best["matched_fields"]
                ),
                "candidate_count": (
                    len(same_score_candidates)
                ),
                "data": None
            }

        # ====================================================
        # Confidence
        # ====================================================

        score = best["score"]

        # All four fields match.
        if score >= 95:

            confidence = "high"

        # Name + DOB + Town is also considered
        # high confidence because DOB is a strong
        # identity attribute.
        elif (
            score == 85
            and
            "name" in best["matched_fields"]
            and
            "date_of_birth"
            in best["matched_fields"]
            and
            "town"
            in best["matched_fields"]
        ):

            confidence = "high"

        elif score >= 80:

            confidence = "medium"

        else:

            return {
                "status": "not_matched",
                "confidence": "none",
                "score": score,
                "matched_fields": (
                    best["matched_fields"]
                ),
                "data": None
            }

        return {
            "status": "matched",
            "confidence": confidence,
            "score": score,
            "matched_fields": (
                best["matched_fields"]
            ),
            "data": best["record"]
        }
