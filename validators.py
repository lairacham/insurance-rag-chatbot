def validate_quote_data(product: str, data: dict) -> list:
    """
    Validates collected quote data.
    Returns a list of error messages — empty list means all valid.
    """
    errors = []

    if product == "auto":
        # driver_age
        age = data.get("driver_age")
        if age is not None:
            try:
                a = int(age)
                if a < 16:
                    errors.append("Driver must be at least 16 years old.")
                elif a > 100:
                    errors.append("Please enter a valid driver age.")
            except (ValueError, TypeError):
                errors.append("Driver age must be a number (e.g. 28).")

        # vehicle_year
        year = data.get("vehicle_year")
        if year is not None:
            try:
                y = int(year)
                if y > 2026:
                    errors.append("Vehicle year cannot be in the future.")
                elif y < 1970:
                    errors.append("Vehicle year must be 1970 or later.")
            except (ValueError, TypeError):
                errors.append("Vehicle year must be a number (e.g. 2019).")

        # vehicle_make
        make = data.get("vehicle_make")
        if make is not None:
            if len(str(make).strip()) < 2:
                errors.append("Please enter a valid vehicle make (e.g. Toyota).")

        # vehicle_model
        model = data.get("vehicle_model")
        if model is not None:
            if len(str(model).strip()) < 1:
                errors.append("Please enter a valid vehicle model (e.g. Camry).")

        # driving_history
        history = data.get("driving_history")
        valid_histories = ["clean", "minor_violation", "at_fault_accident", "multiple_violations", "dui"]
        if history is not None and str(history).lower() not in valid_histories:
            errors.append(f"Driving history must be one of: {', '.join(valid_histories)}.")

        # coverage_level
        coverage = data.get("coverage_level")
        valid_coverages = ["basic", "standard", "comprehensive"]
        if coverage is not None and str(coverage).lower() not in valid_coverages:
            errors.append(f"Coverage level must be one of: {', '.join(valid_coverages)}.")

    elif product == "home":
        # property_type
        prop = data.get("property_type")
        valid_types = ["single-family", "townhouse", "condo", "manufactured"]
        if prop is not None and str(prop).lower() not in valid_types:
            errors.append(f"Property type must be one of: {', '.join(valid_types)}.")

        # location
        location = data.get("location")
        if location is not None:
            if len(str(location).strip()) < 3:
                errors.append("Please enter a valid location (e.g. Austin, TX).")

        # home_value
        value = data.get("home_value")
        if value is not None:
            try:
                v = float(str(value).replace(",", "").replace("$", ""))
                if v < 50000:
                    errors.append("Home value must be at least $50,000.")
                elif v > 10000000:
                    errors.append("Home value cannot exceed $10,000,000.")
            except (ValueError, TypeError):
                errors.append("Home value must be a number (e.g. 350000).")

        # coverage_level
        coverage = data.get("coverage_level")
        valid_coverages = ["basic", "standard", "comprehensive"]
        if coverage is not None and str(coverage).lower() not in valid_coverages:
            errors.append(f"Coverage level must be one of: {', '.join(valid_coverages)}.")

    elif product == "life":
        # applicant_age
        age = data.get("applicant_age")
        if age is not None:
            try:
                a = int(age)
                if a < 18:
                    errors.append("Applicant must be at least 18 years old.")
                elif a > 75:
                    errors.append("Maximum application age is 75.")
            except (ValueError, TypeError):
                errors.append("Age must be a number (e.g. 35).")

        # smoker
        smoker = data.get("smoker")
        if smoker is not None:
            if isinstance(smoker, str):
                if smoker.lower() not in ("true", "false", "yes", "no"):
                    errors.append("Please answer yes or no for smoker status.")

        # health_status
        health = data.get("health_status")
        valid_health = ["excellent", "good", "fair", "poor"]
        if health is not None and str(health).lower() not in valid_health:
            errors.append(f"Health status must be one of: {', '.join(valid_health)}.")

        # coverage_amount
        amount = data.get("coverage_amount")
        if amount is not None:
            try:
                c = float(str(amount).replace(",", "").replace("$", ""))
                if c < 100000:
                    errors.append("Minimum coverage amount is $100,000.")
                elif c > 5000000:
                    errors.append("Maximum coverage amount is $5,000,000.")
            except (ValueError, TypeError):
                errors.append("Coverage amount must be a number (e.g. 500000).")

        # term_length
        term = data.get("term_length")
        if term is not None:
            try:
                t = int(term)
                if t not in (10, 15, 20, 30):
                    errors.append("Term length must be 10, 15, 20, or 30 years.")
            except (ValueError, TypeError):
                errors.append("Term length must be a number (10, 15, 20, or 30).")

    return errors