# Map processing and rasterization draft

Use `spec_loader.load_spec` with `data/maps/department_v1/map_spec.yaml`, then call `rasterizer.rasterize`. The YAML file uses JSON-compatible syntax so the core loader needs no additional parser dependency. The rasterizer retains the legacy builder's cell-center inclusion, 12 px wall stamping, fill order and start conversion. Map editing helpers operate on array-index rectangles.

`build_department_map_v03.py` is a small wrapper around the shared declarative spec and rasterizer. Image import, preprocessing, calibration, overlay, persistence and optional wall suggestions are separate modules. OpenCV is used only inside optional image functions.
