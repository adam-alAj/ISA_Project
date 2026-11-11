"""P2 map processing and environment contract tests."""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path

import numpy as np
import pytest

from src.environment.cleaning_state import CleaningState
from src.environment.components import connected_components, reachable_from
from src.environment.coords import cell_to_meters, cell_to_pixel_center, cell_to_world, meters_to_cell, pixel_to_cell
from src.environment.grid_map import GridMap
from src.environment.validation import validate_cells, validate_map
from src.map_processing.calibration import calibrate_least_squares, calibrate_two_points
from src.map_processing.constants import CellState as S
from src.map_processing.map_io import load_map, save_map
from src.map_processing.preprocess import preprocess_image
from src.map_processing.rasterizer import MapEditor, rasterize
from src.map_processing.spec_loader import load_spec
from tests.maps import synthetic


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "data/maps/department_v1/map_spec.yaml"
V02_PATH = ROOT / "data/maps/department_v0_2/department_map.npy"
V02_NPY_SHA256 = "4A9653FFFA536926CA5FA06FE833C96429D6FB30F98391F1518DE7FBE1127EDB"
V03_PATH = ROOT / "data/maps/department_v0_3/department_map.npy"
V03_NPY_SHA256 = "8D1394701FEA02122D8145117FFAC62C407D4237D9436901224F052B77EC4158"


def test_spec_rasterization_reproduces_v03_and_preserves_v02_hall_doors() -> None:
    """The approved P1 geometry correction is exact; its fixed regions match v0.2."""
    spec_bytes = SPEC_PATH.read_bytes()
    result = rasterize(load_spec(SPEC_PATH))
    corrected = np.load(V03_PATH)
    baseline = np.load(V02_PATH)
    assert hashlib.sha256(V02_PATH.read_bytes()).hexdigest().upper() == V02_NPY_SHA256
    np.testing.assert_array_equal(result.grid, corrected)
    buffer = io.BytesIO()
    np.save(buffer, result.grid)
    assert hashlib.sha256(buffer.getvalue()).hexdigest().upper() == V03_NPY_SHA256
    # The only intentional output change is the P1-approved R4/R5/R6 outer-edge correction.
    rows, cols = np.indices(baseline.shape)
    x, y = 80 + (cols + 0.5) * 10.8, 160 + (rows + 0.5) * 10.8
    hall = ((x >= 340) & (x <= 1130) & (y >= 310) & (y <= 855)) | ((x >= 340) & (x <= 905) & (y >= 855) & (y <= 1370)) | ((x >= 340) & (x <= 860) & (y >= 1370) & (y <= 1503))
    np.testing.assert_array_equal(baseline[hall], result.grid[hall])
    np.testing.assert_array_equal(np.argwhere(baseline == S.DOOR), np.argwhere(result.grid == S.DOOR))
    changed = baseline != result.grid
    allowed = (((x >= 1244) & (x <= 1336) & (y >= 209) & (y <= 496)) |
               ((x >= 1299) & (x <= 1326) & (y >= 584) & (y <= 756)) |
               ((x >= 1154) & (x <= 1291) & (y >= 849) & (y <= 1036)))
    assert not np.any(changed & ~allowed)
    assert result.start_cell == (118, 54)
    assert hashlib.sha256(spec_bytes).hexdigest()
    areas = result.metadata["room_areas_m2"]
    equal_group = [areas[room] for room in ("R2", "R3", "R5", "R8")]
    assert all(2.6 * 0.95 <= area <= 2.6 * 1.05 for area in equal_group)
    assert areas["R7"] > areas["R1"] > areas["R4"] > areas["R6"] > max(equal_group)
    areas = result.metadata["room_areas_m2"]
    equal = [areas[key] for key in ("R2", "R3", "R5", "R8")]
    assert all(2.6 * 0.95 <= value <= 2.6 * 1.05 for value in equal)
    assert areas["R7"] > areas["R1"] > areas["R4"] > areas["R6"] > max(equal)


def test_coordinates_and_six_meter_reference() -> None:
    """Coordinate conversions round-trip within half a cell and retain scale."""
    origin, ppm, cell_m = (80.0, 160.0), 108.0, 0.1
    assert pixel_to_cell((665, 1440), origin, ppm, cell_m) == (118, 54)
    assert meters_to_cell((6.0, 6.0), cell_m) == (60, 60)
    assert cell_to_meters((59, 59), cell_m) == pytest.approx((5.95, 5.95))
    point = cell_to_pixel_center((59, 59), origin, ppm, cell_m)
    assert pixel_to_cell(point, origin, ppm, cell_m) == (59, 59)
    assert cell_to_world((0, 0), cell_m) == pytest.approx((0.05, 0.0, -0.05))
    # 54 px / 108 px per metre = 0.5 m, represented by five 10 cm cells.
    assert calibrate_two_points((0, 0), (54, 0), 0.5) == pytest.approx(108.0)
    assert 54 / (108 * cell_m) == pytest.approx(5.0)  # column width, in 10 cm cells
    assert 11 / (108 * cell_m) == pytest.approx(1.0, abs=0.1)  # cabinet protrusion


def test_least_squares_calibration_reports_residuals() -> None:
    result = calibrate_least_squares((545, 648, 97), (5, 6, 0.9))
    assert result.pixels_per_meter == pytest.approx(108.0, abs=1.0)
    assert len(result.residuals_px) == 3
    assert result.rms_residual_px >= 0


def test_preprocessing_keeps_source_coordinate_transform() -> None:
    image = np.arange(100, dtype=np.uint8).reshape(10, 10)
    transformed = preprocess_image(image, crop_xywh=(2, 3, 5, 4))
    assert transformed.image.shape == (4, 5)
    source = transformed.processed_to_source @ np.array([1.0, 1.0, 1.0])
    assert source[:2] == pytest.approx((3.0, 4.0))
    point = np.array([2.0, 1.0, 1.0])
    restored = transformed.source_to_processed @ (transformed.processed_to_source @ point)
    assert restored == pytest.approx(point)


@pytest.mark.parametrize("orientation", range(1, 9))
def test_exif_orientation_matrix_maps_processed_pixels_to_source(orientation: int) -> None:
    image = np.arange(6, dtype=np.uint8).reshape(2, 3)
    transformed = preprocess_image(image, exif_orientation=orientation)
    for row in range(transformed.image.shape[0]):
        for col in range(transformed.image.shape[1]):
            source_xy = transformed.processed_to_source @ np.array([col, row, 1.0])
            source_col, source_row = map(int, source_xy[:2])
            assert transformed.image[row, col] == image[source_row, source_col]


def test_neighbors_and_transitions_never_enter_blocked_cells() -> None:
    grid = np.array([[0, 3, 1], [0, 2, 0], [1, 0, 0]], dtype=np.uint8)
    world = GridMap(grid, 0.1)
    assert list(world.neighbors((0, 0))) == [(0, 1), (1, 0)]
    assert not world.is_valid_transition((0, 0), (0, 2))
    assert not world.is_valid_transition((0, 0), (1, 1))
    for cell in map(tuple, np.argwhere(np.isin(grid, (1, 2)))):
        assert not world.is_traversable(cell)


def test_cleaning_state_is_separate_and_component_detection_works() -> None:
    grid = synthetic.disconnected()
    occupancy_before = grid.copy()
    cleaning = CleaningState(grid.shape)
    cleaning.mark_cleaned([(0, 0), (0, 1)])
    assert cleaning.is_cleaned((0, 0)) and cleaning.count() == 2
    np.testing.assert_array_equal(grid, occupancy_before)
    labels, count = connected_components(grid == S.FREE)
    assert count == 2 and labels[0, 0] != labels[0, -1]
    reached = reachable_from(grid == S.FREE, (0, 0))
    assert reached[0, 0] and not reached[0, -1]


def test_footprint_inflation_clips_edges_and_preserves_department_rooms() -> None:
    result = rasterize(load_spec(SPEC_PATH))
    world = GridMap(result.grid, 0.1, (80, 160), result.metadata)
    nav = world.with_footprint(0.175)
    assert nav.shape == result.grid.shape
    assert not nav[0, 0]
    reached = reachable_from(nav, result.start_cell)
    for bounds in load_spec(SPEC_PATH)["rooms"].values():
        xmin, ymin, xmax, ymax = bounds
        rows, cols = np.indices(nav.shape)
        x = 80 + (cols + 0.5) * 10.8
        y = 160 + (rows + 0.5) * 10.8
        room = (x >= xmin) & (x <= xmax) & (y >= ymin) & (y <= ymax)
        assert np.any(room & reached)
    # The entrance cabinet does not sever the open hall/entrance connection.
    # Column 25 lies within the conservative inflated clearance envelope;
    # column 27 is the first reachable centre cell beyond the cabinet.
    assert reached[118, 54] and reached[118, 27]


def test_validation_structures_invalid_start_and_targets() -> None:
    grid = GridMap(np.array([[0, 1], [3, 2]], dtype=np.uint8), 0.1)
    issues = validate_cells(grid, (0, 1), [(8, 8), (0, 0)])
    assert {issue.code for issue in issues} == {"cell_not_traversable", "cell_out_of_bounds"}
    assert all(issue.severity == "error" for issue in issues)
    assert validate_map(grid, (0, 0))


def test_editor_operations_are_explicit_and_bounded() -> None:
    editor = MapEditor(np.zeros((3, 3), dtype=np.uint8))
    editor.add_door((1, 1, 2, 2))
    editor.add_obstacle((0, 0, 1, 1))
    assert editor.grid[1, 1] == S.DOOR and editor.grid[0, 0] == S.OCCUPIED
    with pytest.raises(ValueError):
        editor.set_cells((-1, 0, 1, 1), S.FREE)


def test_map_bundle_round_trip_and_schema_validation(tmp_path: Path) -> None:
    grid = np.array([[0, 3], [1, 0]], dtype=np.uint8)
    hashes = save_map(tmp_path, grid, {"version": "test", "cell_m": 0.1, "start_cell": [0, 0]}, b"spec")
    repeated = save_map(tmp_path, grid, {"version": "test", "cell_m": 0.1, "start_cell": [0, 0]}, b"spec")
    assert hashes["grid.npz"] == repeated["grid.npz"]
    restored, metadata = load_map(tmp_path)
    np.testing.assert_array_equal(restored, grid)
    assert metadata["schema_version"] == 1 and metadata["spec_sha256"]
    assert set(hashes) == {"map.json", "grid.npz"}
    document = json.loads((tmp_path / "map.json").read_text())
    document["grid_npz_sha256"] = document["grid_npz_sha256"].upper()
    (tmp_path / "map.json").write_text(json.dumps(document))
    load_map(tmp_path)  # hexadecimal digest casing does not affect integrity
    document = json.loads((tmp_path / "map.json").read_text())
    document["schema_version"] = 99
    (tmp_path / "map.json").write_text(json.dumps(document))
    with pytest.raises(ValueError):
        load_map(tmp_path)


@pytest.mark.parametrize("factory", [synthetic.open_room, synthetic.corridor, synthetic.wall_detour,
                                     synthetic.disconnected, synthetic.narrow_passage,
                                     synthetic.heuristic_trap, synthetic.weighted_cost])
def test_synthetic_map_fixtures_are_valid_arrays(factory) -> None:
    grid = factory()
    assert grid.dtype == np.uint8 and grid.ndim == 2
    assert set(np.unique(grid)).issubset({0, 1, 2, 3})
