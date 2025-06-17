// main.scad
// OpenSCAD assembly for SWIR imaging station
// All components aligned along z-axis (optical axis)

// User-set variables for actual part lengths (adjust as needed)
tube_lens_length = 50;        // mm, physical length of TTL200-S8 tube lens (adjust to actual)
profiler_length = 45;         // mm, estimated for beam profiler
tube_to_camera_flange = 148;  // mm, optical spacing: tube lens rear face to camera flange

// 1. Import Camera at origin
translate([0,0,0])
    import("stl/camera.stl");

// 2. Import Tube Lens: Place its rear face tube_to_camera_flange mm in front of camera flange
translate([0,0,tube_to_camera_flange])
    import("stl/tube.stl");

// 3. Import Beam Profiler: Place it in front of tube lens (adjust distance as needed for your setup)
translate([0,0,tube_to_camera_flange + tube_lens_length])
    import("stl/profiler.stl");

// You may need to adjust the tube_lens_length and profiler_length values to match your actual STEP files!
// For visualization only: you can add color() wrappers or axis markers if desired

