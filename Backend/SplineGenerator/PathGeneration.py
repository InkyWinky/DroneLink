import PointToPointPathGeneration as ptpPG
import SearchPathGeneration as saPG

class PathGenerationType:
    SEARCH_AREA = "saPG"
    POINT_TO_POINT = "ptpPG"

class PathGeneration:
    def __init__(self):
        # Type of path generation
        self.path_generation_type = None

        # All relevant plane and world parameters
        pass

    def generate_path(self):
        # Check what type of path generation is desired
        if self.path_generation_type == "saPG":  # Search area path generation
            self.handle_saPG()

        if self.path_generation_type == "ptpPG":  # Point to point path generation
            self.handle_ptpPG()