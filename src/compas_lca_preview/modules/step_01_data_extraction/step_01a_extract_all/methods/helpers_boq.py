# Extract volume, area, and length from best available source (1. IFC / 2. Pset/ 3. Bounding Box).

def extract_quantities(volume_compas, element_entity, ifc_quants_element, psets_element, obb_dimensions):
    volume = None
    area = None
    length = None

    volume_source = "Not available"
    area_source = "Not available"
    length_source = "Not available"

    # ==== Volume Calculation ====
    if isinstance(ifc_quants_element, dict):
        volume = ifc_quants_element.get("Net Volume")
        if volume is not None:
            try:
                volume = round(volume,4)
                volume_source = "(P1) IFC Quantities"
            except (ValueError, TypeError):
                volume = None

    if volume is None and volume_compas is not None:
        volume = round(volume_compas, 4)
        volume_source = "(P2) COMPAS Brep"

    if volume is None and isinstance(psets_element, dict):
        volume = psets_element.get("Volume") or psets_element.get("Volumen")
        try:
            volume = round(float(volume),4)
            volume_source = "(P3) Pset Quantities"
        except (ValueError, TypeError):
            volume = None

    if volume is None and isinstance(obb_dimensions, dict):
        obb_values = [obb_dimensions.get(axis) for axis in ("X", "Y", "Z") if obb_dimensions.get(axis) is not None]
        if len(obb_values) == 3:
            try:
                x, y, z = obb_values
                volume = round(x * y * z, 4)
                volume_source = "(P4) Bounding Box Volume"
            except (ValueError, TypeError):
                volume = None

    # ==== Area Calculation ====
    if isinstance(ifc_quants_element, dict):
        if element_entity in ("IfcSlab", "IfcRoof", "IfcCovering", "IfcStair", "IfcStairFlight", "IfcRamp", "IfcFooting"):
            area = ifc_quants_element.get("Net Footprint Area")
        else:
            area = ifc_quants_element.get("Net Side Area")
        if area is not None:
            try:
                area = round(area, 4)
                area_source = "(P1) IFC Quantities"
            except (ValueError, TypeError):
                area = None

    if area is None and isinstance(obb_dimensions, dict):
        obb_values = [obb_dimensions.get(axis) for axis in ("X", "Y", "Z") if obb_dimensions.get(axis) is not None]
        if obb_values and len(obb_values) == 3:
            x, y, z = obb_values
            surfaces = [x * y, x * z, y * z]
            area = round(max(surfaces), 4)
            area_source = "(P2) Bounding Box Surface"

    if area is None and isinstance(psets_element, dict):
        area = psets_element.get("Area") or psets_element.get("Fläche")
        try:
            area = round(float(area), 4)
            area_source = "(P3) Pset Quantities"
        except (ValueError, TypeError):
            area = None

    # ==== Length Calculation ====
    if isinstance(ifc_quants_element, dict):
        length = ifc_quants_element.get("Length")
        if length is not None:
            try:
                length = round(length, 4)
                length_source = "(P1) IFC Quantities"
            except (ValueError, TypeError):
                length = None

    if length is None and isinstance(obb_dimensions, dict):
        obb_values = [obb_dimensions.get(axis) for axis in ("X", "Y", "Z") if obb_dimensions.get(axis) is not None]
        if obb_values and len(obb_values) == 3:
            length = round(max(obb_values), 4)
            length_source = "(P2) Bounding Box Length"

    if length is None and isinstance(psets_element, dict):
        length = psets_element.get("Length") or psets_element.get("Länge")
        try:
            length = round(float(length), 4)
            length_source = "(P3) Pset Quantities"
        except (ValueError, TypeError):
            length = None

    return volume, area, length, volume_source, area_source, length_source
