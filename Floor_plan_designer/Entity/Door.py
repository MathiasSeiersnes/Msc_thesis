from ifcopenshell import guid

class Door:
    def __init__(self, file, wall, position, size=(250, 1000)):
        self.file = file
        self.wall = wall  # This must be the actual IfcWall entity
        self.size = size  # (width, height)
        self.position = position
        
        self.position.append(0.0)
        

    def create(self):
        opening_guid = guid.new()
        opening = self.file.create_entity("IfcOpeningElement",
                                          GlobalId=opening_guid,
                                          Name="Opening")

        # Create profile and extrusion for the void
        profile = self.file.create_entity("IfcRectangleProfileDef",
                                          ProfileType="AREA",
                                          XDim=self.size[0],
                                          YDim=self.size[1])

        # Extrude in Z direction (into the wall)
        extrusion_direction = self.file.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0))
        position = self.file.create_entity("IfcAxis2Placement3D")

        body = self.file.create_entity("IfcExtrudedAreaSolid",
                                       SweptArea=profile,
                                       Position=position,
                                       ExtrudedDirection=extrusion_direction,
                                       Depth=2200)

        shape_rep = self.file.create_entity("IfcShapeRepresentation",
                                            RepresentationIdentifier="Body",
                                            RepresentationType="SweptSolid",
                                            Items=[body])

        product_rep = self.file.create_entity("IfcProductDefinitionShape",
                                              Representations=[shape_rep])

        opening.Representation = product_rep

        # Local placement relative to wall
        cartesian_point = self.file.create_entity("IfcCartesianPoint", [float(x) for x in self.position])
        axis = self.file.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0))
        ref_dir = self.file.create_entity("IfcDirection", DirectionRatios=(1.0, 0.0, 0.0))

        rel_placement = self.file.create_entity("IfcAxis2Placement3D",
                                                Location=cartesian_point,
                                                Axis=axis,
                                                RefDirection=ref_dir)

        local_placement = self.file.create_entity("IfcLocalPlacement",
                                                  PlacementRelTo=self.wall.ObjectPlacement,
                                                  RelativePlacement=rel_placement)

        opening.ObjectPlacement = local_placement

        # Link the opening to the wall
        self.file.create_entity("IfcRelVoidsElement",
                                GlobalId=guid.new(),
                                RelatingBuildingElement=self.wall,
                                RelatedOpeningElement=opening)

        return self.file
