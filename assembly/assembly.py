import FreeCAD as App
import Import

doc = App.newDocument("Assembly")

# Paths to your files (adjust paths if needed)
camera_path = "/mnt/data/camera.STEP"
profiler_path = "/mnt/data/profiler.stp"

# Import
Import.insert(camera_path, doc.Name)
Import.insert(profiler_path, doc.Name)
