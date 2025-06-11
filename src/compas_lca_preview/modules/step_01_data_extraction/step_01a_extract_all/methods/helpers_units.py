# Extracts the length conversion factor from the model's unit assignments.
# Returns a float representing the multiplier to convert to meters.

def model_units(model):
    """
    Extracts only relevant units from the model and returns a dictionary with units
    and a length conversion factor.
    """
    try:
        unit_assignments = model.get_entities_by_type("IfcUnitAssignment")
        formatted_units = {}
        length_conversion_factor = 1.0  # Default to METRE (no conversion)

        # Define the relevant unit types to extract
        relevant_units = {
            "LENGTHUNIT", "AREAUNIT", "VOLUMEUNIT",
            "PLANEANGLEUNIT", "MASSUNIT", "MASSDENSITYUNIT"
        }

        for assignment in unit_assignments:
            for unit in getattr(assignment, "Units", []):
                unit_type = getattr(unit, "UnitType", "Unknown")

                # Only store relevant unit types
                if unit_type in relevant_units:
                    unit_name = getattr(unit, "Name", "Unknown").upper()
                    unit_prefix = getattr(unit, "Prefix", None)  # Optional prefix (MILLI, CENTI, etc.)

                    # Convert prefix if present
                    unit_prefix = unit_prefix.upper() if isinstance(unit_prefix, str) else ""

                    # Store unit type
                    formatted_units[unit_type] = unit_name

                    # Handle unit conversion for length (if necessary)
                    if unit_type == "LENGTHUNIT":
                        if unit_prefix == "MILLI":
                            length_conversion_factor = 0.001  # Convert from mm to meters
                            formatted_units["LENGTHUNIT"] = "MILLIMETRE"
                        elif unit_prefix == "CENTI":
                            length_conversion_factor = 0.01  # Convert from cm to meters
                            formatted_units["LENGTHUNIT"] = "CENTIMETRE"
                        else:
                            formatted_units["LENGTHUNIT"] = "METRE"  # Default to meters

        return formatted_units, length_conversion_factor  # Return only filtered units

    except Exception as e:
        print(f"Error extracting units: {e}")
        return {
            "LENGTHUNIT": "METRE",
            "AREAUNIT": "SQUARE_METRE",
            "VOLUMEUNIT": "CUBIC_METRE",
            "PLANEANGLEUNIT": "DEGREE",
            "MASSUNIT": "KILOGRAM",
            "MASSDENSITYUNIT": "KILOGRAM_PER_CUBIC_METRE"
        }, 1.0  # Default to reasonable unit values if extraction fails