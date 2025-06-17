import FreeCAD as App
import Import
import os

macro_dir = os.path.dirname(os.path.realpath(__file__))
step_dir = os.path.join(macro_dir, "step")

camera_path = os.path.join(step_dir, "Goldeye G-033 SWIR TEC1.STEP")
tube_lens_path = os.path.join(step_dir, "TTL200-S8-Step.step")
profiler_path = os.path.join(step_dir, "ophiropt_SP90605.stp")

# === Measured offsets (update these after measuring in FreeCAD!) ===
camera_flange_to_origin = 10          # mm: distance from camera origin to mounting face
tube_lens_rear_to_origin = 5          # mm: distance from tube lens origin to rear face
tube_lens_front_to_origin = 55        # mm: distance from tube lens origin to front face (physical tube length, update to your measure)
profiler_rear_to_origin = 0           # mm: profiler origin to rear face (if origin = rear, set to 0)

doc = App.newDocument("SWIR_Imaging_Assembly")

# Place camera (reference)
camera_obj = Import.insert(camera_path, "SWIR_Imaging_Assembly")
camera_obj = doc.Objects[-1]
camera_obj.Placement.Base = App.Vector(0, 0, 0)
camera_z = 0

# Place tube lens so rear face matches camera flange
z_tube_lens = camera_z + (camera_flange_to_origin - tube_lens_rear_to_origin)
tube_lens_obj = Import.insert(tube_lens_path, "SWIR_Imaging_Assembly")
tube_lens_obj = doc.Objects[-1]
tube_lens_obj.Placement.Base = App.Vector(0, 0, z_tube_lens)

# Place profiler so its rear matches tube lens front
z_profiler = z_tube_lens + (tube_lens_front_to_origin - profiler_rear_to_origin)
profiler_obj = Import.insert(profiler_path, "SWIR_Imaging_Assembly")
profiler_obj = doc.Objects[-1]
profiler_obj.Placement.Base = App.Vector(0, 0, z_profiler)

doc.recompute()
