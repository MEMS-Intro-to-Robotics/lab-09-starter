#!/usr/bin/env python3
"""
Autograding validation for Lab 9: Autonomous Maze Exploration and SLAM.
Run with: pytest test_lab_9.py -v

Tests are organized into tiers:
  - Required files & structure (hard fail)
  - Python syntax (hard fail)
  - navigate_to_point.py implementation checks (hard fail)
  - autonomous_explore.py implementation checks (hard fail)
  - setup.py entry points (hard fail)
  - Screenshots & git hygiene (warnings)
"""

import ast
import os
import re
import warnings

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
EXPECTED_PKG_PATTERNS = ["turtlebot4", "tb4", "nav", "explore", "slam", "lab09"]

README_STARTER_FINGERPRINT = "Update this README with your name, NetID, and instructions"

EXPECTED_ENTRY_POINTS = {"navigate_to_point", "auto_explore"}
EXPECTED_SCRIPTS = ["navigate_to_point.py", "autonomous_explore.py"]


# ── Helpers ──────────────────────────────────────────────────


def _find_ros2_package():
    """Find the ROS 2 package directory under ros2_ws/src/."""
    src_dir = os.path.join("ros2_ws", "src")
    if not os.path.isdir(src_dir):
        return None
    for entry in os.listdir(src_dir):
        entry_lower = entry.lower()
        if any(p in entry_lower for p in EXPECTED_PKG_PATTERNS):
            full = os.path.join(src_dir, entry)
            if os.path.isdir(full):
                return full
    # Fallback: first directory with package.xml
    for entry in os.listdir(src_dir):
        full = os.path.join(src_dir, entry)
        if os.path.isdir(full) and os.path.isfile(os.path.join(full, "package.xml")):
            return full
    return None


def _find_file_in_package(name):
    """Search for a file anywhere in the package directory tree."""
    pkg = _find_ros2_package()
    if pkg is None:
        return None
    for root, _dirs, files in os.walk(pkg):
        if name in files:
            return os.path.join(root, name)
    return None


def _find_python_files(pkg_dir):
    """Return all non-boilerplate .py files in the package."""
    py_files = []
    for root, _dirs, files in os.walk(pkg_dir):
        for f in files:
            if f.endswith(".py") and f not in ("setup.py", "__init__.py", "conftest.py"):
                py_files.append(os.path.join(root, f))
    return py_files


def _get_images(docs_dir="docs"):
    if not os.path.isdir(docs_dir):
        return []
    return [
        f for f in os.listdir(docs_dir)
        if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS
    ]


def _check_syntax(path):
    with open(path, "r", errors="replace") as f:
        source = f.read()
    ast.parse(source, filename=path)


def _read_source(path):
    if path is None or not os.path.isfile(path):
        return None, None
    with open(path, "r", errors="replace") as f:
        source = f.read()
    try:
        tree = ast.parse(source, filename=path)
    except SyntaxError:
        return source, None
    return source, tree


def _get_navigate_source():
    """Find and read navigate_to_point.py."""
    path = _find_file_in_package("navigate_to_point.py")
    return _read_source(path)


def _get_explore_source():
    """Find and read autonomous_explore.py."""
    path = _find_file_in_package("autonomous_explore.py")
    return _read_source(path)


# ── Required files & structure (hard fail) ───────────────────


class TestRepositoryStructure:
    """Verify the expected repository layout exists."""

    def test_readme_exists(self):
        assert os.path.isfile("README.md"), "README.md not found"

    def test_readme_not_empty(self):
        assert os.path.getsize("README.md") > 0, "README.md is empty"

    def test_readme_updated(self):
        with open("README.md", "r", errors="replace") as f:
            content = f.read()
        assert README_STARTER_FINGERPRINT not in content, (
            "README.md still contains the starter template text. "
            "Please update it with your name, NetID, and instructions for running your code."
        )

    def test_docs_directory_exists(self):
        assert os.path.isdir("docs"), "docs/ directory not found"

    def test_ros2_src_exists(self):
        assert os.path.isdir(os.path.join("ros2_ws", "src")), "ros2_ws/src/ not found"

    def test_ros2_package_found(self):
        pkg = _find_ros2_package()
        assert pkg is not None, (
            "No ROS 2 package found under ros2_ws/src/. "
            "Expected a package directory matching one of: "
            + ", ".join(EXPECTED_PKG_PATTERNS)
        )
        print(f"Found package: {os.path.basename(pkg)}")

    def test_setup_py_exists(self):
        pkg = _find_ros2_package()
        if pkg is None:
            return
        assert os.path.isfile(os.path.join(pkg, "setup.py")), (
            "setup.py not found in package"
        )

    def test_package_xml_exists(self):
        pkg = _find_ros2_package()
        if pkg is None:
            return
        assert os.path.isfile(os.path.join(pkg, "package.xml")), (
            "package.xml not found in package"
        )

    def test_navigate_to_point_exists(self):
        path = _find_file_in_package("navigate_to_point.py")
        assert path is not None, (
            "navigate_to_point.py not found in package. "
            "This script should send navigation goals to Nav2."
        )

    def test_autonomous_explore_exists(self):
        path = _find_file_in_package("autonomous_explore.py")
        assert path is not None, (
            "autonomous_explore.py not found in package. "
            "This script should implement frontier-based exploration."
        )


# ── Python syntax (hard fail) ───────────────────────────────


class TestPythonSyntax:
    """All Python files must parse without syntax errors."""

    def test_all_python_syntax(self):
        pkg = _find_ros2_package()
        if pkg is None:
            return
        errors = []
        for pf in _find_python_files(pkg):
            try:
                _check_syntax(pf)
            except SyntaxError as e:
                errors.append(f"{pf}: {e}")
        assert not errors, (
            "Syntax errors found:\n" + "\n".join(errors)
        )


# ── navigate_to_point.py checks (hard fail) ─────────────────


class TestNavigateToPoint:
    """Verify navigate_to_point.py has the required implementation."""

    def test_imports_rclpy(self):
        source, _ = _get_navigate_source()
        assert source is not None, "Could not read navigate_to_point.py"
        assert "rclpy" in source, (
            "navigate_to_point.py does not import rclpy. "
            "All ROS 2 Python nodes must import rclpy."
        )

    def test_uses_turtlebot4_navigator(self):
        source, _ = _get_navigate_source()
        assert source is not None, "Could not read navigate_to_point.py"
        assert "TurtleBot4Navigator" in source, (
            "navigate_to_point.py does not use TurtleBot4Navigator. "
            "This helper class simplifies sending goals to Nav2."
        )

    def test_creates_navigation_goal(self):
        """Must construct a PoseStamped goal or use getPoseStamped."""
        source, _ = _get_navigate_source()
        assert source is not None, "Could not read navigate_to_point.py"
        has_goal = (
            "PoseStamped" in source
            or "getPoseStamped" in source
        )
        assert has_goal, (
            "No navigation goal construction found. "
            "You must create a PoseStamped goal or use nav.getPoseStamped()."
        )

    def test_sends_goal(self):
        """Must call startToPose to dispatch the goal."""
        source, _ = _get_navigate_source()
        assert source is not None, "Could not read navigate_to_point.py"
        assert "startToPose" in source, (
            "No call to startToPose() found. "
            "You must send your goal to Nav2 using nav.startToPose(goal)."
        )

    def test_waits_for_completion(self):
        """Must wait for the navigation task to finish."""
        source, _ = _get_navigate_source()
        assert source is not None, "Could not read navigate_to_point.py"
        assert "isTaskComplete" in source, (
            "No call to isTaskComplete() found. "
            "Your node must wait for Nav2 to finish navigating before proceeding."
        )

    def test_has_random_goals(self):
        """Part B requires random goal generation (loop + random)."""
        source, _ = _get_navigate_source()
        assert source is not None, "Could not read navigate_to_point.py"
        has_random = "random" in source.lower()
        has_loop = "for " in source or "while " in source
        assert has_random and has_loop, (
            "navigate_to_point.py should include random goal generation with a loop "
            "(Part B). Expected 'random' import and a for/while loop sending multiple goals."
        )

    def test_has_main_function(self):
        source, _ = _get_navigate_source()
        assert source is not None, "Could not read navigate_to_point.py"
        assert "def main" in source, (
            "No main() function found. "
            "Your script needs a main() function registered as an entry point."
        )


# ── autonomous_explore.py checks (hard fail) ────────────────


class TestAutonomousExplore:
    """Verify autonomous_explore.py has the required implementation."""

    def test_imports_rclpy(self):
        source, _ = _get_explore_source()
        assert source is not None, "Could not read autonomous_explore.py"
        assert "rclpy" in source, (
            "autonomous_explore.py does not import rclpy."
        )

    def test_imports_node(self):
        """Must import Node for class-based node pattern."""
        source, _ = _get_explore_source()
        assert source is not None, "Could not read autonomous_explore.py"
        assert "Node" in source, (
            "autonomous_explore.py does not import or reference Node. "
            "This script should use a class-based node (inheriting from rclpy.node.Node)."
        )

    def test_uses_turtlebot4_navigator(self):
        source, _ = _get_explore_source()
        assert source is not None, "Could not read autonomous_explore.py"
        assert "TurtleBot4Navigator" in source, (
            "autonomous_explore.py does not use TurtleBot4Navigator."
        )

    def test_imports_occupancy_grid(self):
        """Must import OccupancyGrid to process the map."""
        source, _ = _get_explore_source()
        assert source is not None, "Could not read autonomous_explore.py"
        assert "OccupancyGrid" in source, (
            "OccupancyGrid not found in autonomous_explore.py. "
            "You must import nav_msgs.msg.OccupancyGrid to subscribe to the /map topic."
        )

    def test_subscribes_to_map(self):
        """Must create a subscription to the /map topic."""
        source, _ = _get_explore_source()
        assert source is not None, "Could not read autonomous_explore.py"
        has_map_sub = (
            "create_subscription" in source
            and ("map" in source.lower())
        )
        assert has_map_sub, (
            "No subscription to the /map topic found. "
            "Your node must subscribe to OccupancyGrid messages on the /map topic."
        )

    def test_has_map_callback(self):
        """Must have a callback to process incoming map data."""
        source, _ = _get_explore_source()
        assert source is not None, "Could not read autonomous_explore.py"
        has_callback = (
            "map_callback" in source
            or "mapCallback" in source
            or "map_cb" in source
            or "callback" in source.lower()
        )
        assert has_callback, (
            "No map callback function found. "
            "Your node needs a callback to process OccupancyGrid messages."
        )

    def test_uses_numpy_for_map(self):
        """Map processing should use numpy for the occupancy grid."""
        source, _ = _get_explore_source()
        assert source is not None, "Could not read autonomous_explore.py"
        has_numpy = "numpy" in source or "import np" in source or "as np" in source
        assert has_numpy, (
            "numpy not imported. The occupancy grid should be reshaped into a "
            "2D numpy array for efficient frontier detection."
        )

    def test_has_frontier_detection(self):
        """Must implement frontier detection logic."""
        source, _ = _get_explore_source()
        assert source is not None, "Could not read autonomous_explore.py"
        source_lower = source.lower()
        has_frontier = (
            "frontier" in source_lower
            or "unknown" in source_lower
            or "== -1" in source
            or "==-1" in source
        )
        assert has_frontier, (
            "No frontier detection logic found. "
            "Your node must identify frontier cells (unknown cells adjacent to free space). "
            "Look for cells with value -1 in the occupancy grid."
        )

    def test_has_free_space_check(self):
        """Frontier detection requires checking for free space (value 0)."""
        source, _ = _get_explore_source()
        assert source is not None, "Could not read autonomous_explore.py"
        has_free_check = (
            "== 0" in source
            or "==0" in source
            or "free" in source.lower()
        )
        assert has_free_check, (
            "No free-space check found. "
            "Frontier cells are unknown cells (-1) adjacent to free cells (0). "
            "Your code must check for free-space neighbors."
        )

    def test_has_timer_or_loop(self):
        """Must have a periodic exploration loop (timer or while loop)."""
        source, _ = _get_explore_source()
        assert source is not None, "Could not read autonomous_explore.py"
        has_periodic = (
            "create_timer" in source
            or "timer" in source.lower()
            or "while" in source
        )
        assert has_periodic, (
            "No periodic exploration loop found. "
            "Your node should use create_timer() or a while loop to repeatedly "
            "check for frontiers and send new goals."
        )

    def test_converts_grid_to_world_coords(self):
        """Must convert grid cell indices to world coordinates for navigation."""
        source, _ = _get_explore_source()
        assert source is not None, "Could not read autonomous_explore.py"
        has_conversion = (
            "resolution" in source
            or "origin" in source
            or "map_origin" in source
            or "map_resolution" in source
        )
        assert has_conversion, (
            "No grid-to-world coordinate conversion found. "
            "You must convert occupancy grid cell indices to world coordinates "
            "using the map's resolution and origin before sending a goal."
        )

    def test_sends_goal(self):
        """Must send navigation goals."""
        source, _ = _get_explore_source()
        assert source is not None, "Could not read autonomous_explore.py"
        assert "startToPose" in source, (
            "No call to startToPose() found. "
            "Your explorer must send frontier goals to Nav2."
        )

    def test_has_class_definition(self):
        """Part C requires a class-based node."""
        source, tree = _get_explore_source()
        assert source is not None, "Could not read autonomous_explore.py"
        assert tree is not None, "autonomous_explore.py has syntax errors"
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        assert len(classes) > 0, (
            "No class definition found. "
            "autonomous_explore.py should use a class-based node pattern "
            "(e.g., class AutonomousExplorer(Node):)."
        )

    def test_uses_spin(self):
        """Class-based nodes should use rclpy.spin()."""
        source, _ = _get_explore_source()
        assert source is not None, "Could not read autonomous_explore.py"
        assert "spin" in source, (
            "No call to rclpy.spin() found. "
            "A class-based node with subscriptions and timers must be spun "
            "to process callbacks."
        )

    def test_has_main_function(self):
        source, _ = _get_explore_source()
        assert source is not None, "Could not read autonomous_explore.py"
        assert "def main" in source, (
            "No main() function found. "
            "Your script needs a main() function registered as an entry point."
        )


# ── setup.py entry points (hard fail) ───────────────────────


class TestSetupEntryPoints:
    """Verify that both scripts are registered as entry points in setup.py."""

    def test_entry_points_registered(self):
        pkg = _find_ros2_package()
        if pkg is None:
            return
        setup_path = os.path.join(pkg, "setup.py")
        if not os.path.isfile(setup_path):
            return
        with open(setup_path, "r", errors="replace") as f:
            content = f.read()
        missing = {ep for ep in EXPECTED_ENTRY_POINTS if ep not in content}
        assert not missing, (
            f"Entry points not found in setup.py: {', '.join(sorted(missing))}. "
            f"Expected entry points for: navigate_to_point, auto_explore. "
            f"Add them to the 'console_scripts' list in setup.py."
        )


# ── Screenshots (warnings) ──────────────────────────────────


class TestScreenshots:
    """Check for documentation screenshots."""

    def test_screenshot_count(self):
        images = _get_images()
        print(f"\nFound {len(images)} image(s) in docs/:")
        for img in sorted(images):
            print(f"  - {img}")
        if len(images) < 3:
            warnings.warn(
                f"Expected at least 3 screenshots (point nav, random goals, "
                f"exploration), found {len(images)}"
            )


# ── Git hygiene (warnings) ──────────────────────────────────


class TestGitHygiene:
    """Check for common git mistakes."""

    def test_gitignore_exists(self):
        if not os.path.isfile(".gitignore"):
            warnings.warn(
                ".gitignore not found - build/, install/, log/ should be excluded"
            )

    def test_no_build_artifacts(self):
        for d in ["build", "install", "log"]:
            for base in [".", "ros2_ws"]:
                path = os.path.join(base, d)
                if os.path.isdir(path):
                    warnings.warn(
                        f"'{path}' is committed - should be in .gitignore"
                    )
