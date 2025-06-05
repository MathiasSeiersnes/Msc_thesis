from ifcopenshell import guid
import math


class Wall:
    def __init__(self, file, start, stop, level=1):
        self.file = file
        self.width = 200
        self.height = 2760 #Height per level - 240
        self.level = str(level)
        
        
        
        self.length = float(math.sqrt((start[0] - stop[0])**2+(start[1] - stop[1])**2))
        self.pos = (float((start[0] + stop[0])/2), float((start[1] + stop[1])/2))
        self.dir = (float(start[1] - stop[1]), float(start[0]-stop[0]), 0.0)
        
    def create(self):
        self.guid = guid.new()
        new_wall = self.file.create_entity("IfcWall", GlobalId=self.guid, Name="New Wall on Level 1")
        profile = self.file.create_entity("IfcRectangleProfileDef", ProfileType="AREA", XDim=self.width, YDim=self.length)
        
        extrusion_direction = self.file.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0))
        extrusion_depth = self.height
        position = self.file.create_entity("IfcAxis2Placement3D")
        
        extruded_solid = self.file.create_entity(
            "IfcExtrudedAreaSolid",
            SweptArea=profile,
            Position=position,
            ExtrudedDirection=extrusion_direction,
            Depth=extrusion_depth
        )
        
        shape_representation = self.file.create_entity(
            "IfcShapeRepresentation",
            RepresentationIdentifier="Body",
            RepresentationType="SweptSolid",
            Items=[extruded_solid]
        )
        
        product_representation = self.file.create_entity("IfcProductDefinitionShape", Representations=[shape_representation])
        new_wall.Representation = product_representation
        
        level = next(storey for storey in self.file.by_type("IfcBuildingStorey") if storey.Name == "Level" + self.level)
        
        placement_origin = self.file.create_entity("IfcCartesianPoint", Coordinates=self.pos)
        axis_direction = self.file.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0))
        ref_direction = self.file.create_entity("IfcDirection", DirectionRatios=self.dir)
        wall_placement_position = self.file.create_entity("IfcAxis2Placement3D",
                                                         Location=placement_origin,
                                                         Axis=axis_direction,
                                                         RefDirection=ref_direction)

        wall_local_placement = self.file.create_entity("IfcLocalPlacement",
                                                      PlacementRelTo=level.ObjectPlacement,
                                                      RelativePlacement=wall_placement_position)

        new_wall.ObjectPlacement = wall_local_placement

        # Step 7: Add wall to the spatial structure of level 1
        self.file.create_entity("IfcRelContainedInSpatialStructure",
                               GlobalId="new_relation_guid",
                               RelatingStructure=level,
                               RelatedElements=[new_wall])
        
        
        return self.file
        
