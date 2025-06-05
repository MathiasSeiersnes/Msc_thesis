from ifcopenshell import guid

class Room:
    def __init__(self, file, room, label = 1, boundary=0):
        self.start = room[:2]
        self.size = room[2:4]
        self.file = file
        labels = ["Living Room", "Bathroom", "Bedroom", "Kitchen", "Bedroom", "Bedroom", "Hallway"]
        
        self.name = labels[label]
        
        self.center = ()
        for i in range(2):
            num = self.start[i] + self.size[i]/2
            self.center = self.center + (num,)
        self.center = self.center + (0.0,)
        
        self.x1 = [self.start[0], self.start[0], self.start[0] + self.size[0], self.start[0] + self.size[0]]
        self.x2 = [self.start[0], self.start[0] + self.size[0], self.start[0] + self.size[0], self.start[0]]
        self.y1 = [self.start[1], self.start[1] + self.size[1], self.start[1] + self.size[1], self.start[1]]
        self.y2 = [self.start[1] + self.size[1], self.start[1] + self.size[1], self.start[1], self.start[1]]

    def create(self):
        self.guid = guid.new()
        
        # Step 1: Create an IfcSpace
        space = self.file.create_entity(
            "IfcSpace",
            GlobalId=self.guid,
            OwnerHistory=self.file.by_type("IfcOwnerHistory")[0],
            Name=self.name,
            Description="A residential living space"
        )

        # Step 2: Define Object Placement for the IfcSpace
        # Create a local placement manually (origin point)
        local_placement = self.file.create_entity(
            "IfcLocalPlacement",
            PlacementRelTo=None,  # Relative to global origin
            RelativePlacement=self.file.create_entity(
                "IfcAxis2Placement3D",
                Location=self.file.create_entity("IfcCartesianPoint", Coordinates=self.center),
                RefDirection=self.file.create_entity("IfcDirection", DirectionRatios=(1.0, 0.0, 0.0)),
                Axis=self.file.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0))
            )
        )
        space.ObjectPlacement = local_placement

        # Step 3: Add Geometry for the IfcSpace
        # Create a rectangular prism geometry manually
        context = self.file.by_type("IfcGeometricRepresentationContext")[0]

        # Define the shape as an IfcExtrudedAreaSolid
        rect_profile = self.file.create_entity(
            "IfcRectangleProfileDef",
            ProfileType="AREA",
            XDim=self.size[0],  # Length
            YDim=self.size[1]   # Width
        )
        position = self.file.create_entity(
            "IfcAxis2Placement3D",
            Location=self.file.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0))
        )
        extruded_solid = self.file.create_entity(
            "IfcExtrudedAreaSolid",
            SweptArea=rect_profile,
            Position=position,
            ExtrudedDirection=self.file.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
            Depth=2760.0  # Height
        )

        # Wrap the geometry in an IfcShapeRepresentation
        shape_representation = self.file.create_entity(
            "IfcShapeRepresentation",
            ContextOfItems=context,
            RepresentationIdentifier="Body",
            RepresentationType="SweptSolid",
            Items=[extruded_solid]
        )

        # Add the shape to the IfcSpace
        product_representation = self.file.create_entity(
            "IfcProductDefinitionShape",
            Representations=[shape_representation]
        )
        space.Representation = product_representation

        # Step 4: Relate the IfcSpace to an IfcBuildingStorey
        # Find or create a building storey to attach the space
        building_storey = self.file.by_type("IfcBuildingStorey")[0]  # Get the first building storey

        # Relate the space to the building storey
        self.file.create_entity(
            "IfcRelContainedInSpatialStructure",
            GlobalId=guid.new(),
            OwnerHistory=self.file.by_type("IfcOwnerHistory")[0],
            RelatedElements=[space]
        )

        return self.file
        

        
    