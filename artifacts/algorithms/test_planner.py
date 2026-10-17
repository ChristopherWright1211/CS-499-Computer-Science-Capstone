"""Integration checks for the compiled CS 499 course planner."""
from pathlib import Path
from tempfile import TemporaryDirectory
import re
import subprocess

HERE = Path(__file__).resolve().parent
EXE = HERE / "course_planner"
SAMPLE = HERE / "CS 300 ABCU_Advising_Program_Input.csv"


def run(menu):
    result = subprocess.run([str(EXE)], input=menu, text=True,
                            capture_output=True, check=True, timeout=5)
    return result.stdout


def scheduled_numbers(output):
    section = output.split("Recommended prerequisite-respecting order:\n", 1)[1]
    return re.findall(r"^\d+\. ([A-Z0-9]+),", section, re.MULTILINE)


def check_sample():
    output = run(f"1\n{SAMPLE}\n2\n3\ncsci400\n4\n9\n")
    assert "Data loaded successfully (8 courses)." in output
    assert "CSCI400, Large Software Development\nPrerequisites: CSCI301, CSCI350" in output
    order = scheduled_numbers(output)
    assert len(order) == 8 and len(set(order)) == 8
    positions = {number: index for index, number in enumerate(order)}
    for line in SAMPLE.read_text().splitlines():
        number, title, *prerequisites = line.split(",")
        for prerequisite in prerequisites:
            if prerequisite:
                assert positions[prerequisite] < positions[number]
    print("PASS: supplied eight-course data, search, and all prerequisite edges")


def check_rejections():
    cases = {
        "cycle": ("A,Course A,B\nB,Course B,A\n", "Circular prerequisite"),
        "unknown": ("A,Course A,Z\n", "unknown prerequisite: Z"),
        "duplicate": ("A,Course A\nA,Another Course\n", "Duplicate course number: A"),
        "repeated edge": ("A,Course A\nB,Course B,A,A\n", "repeats prerequisite: A"),
    }
    with TemporaryDirectory() as temp:
        for name, (data, message) in cases.items():
            path = Path(temp) / (name + ".csv")
            path.write_text(data)
            output = run(f"1\n{path}\n4\n9\n")
            assert message in output
            assert "Please load the data file first." in output
            output = run(f"1\n{SAMPLE}\n1\n{path}\n4\n9\n")
            assert message in output
            assert len(scheduled_numbers(output)) == 8
        print("PASS: cycle, unknown course, duplicate course/edge, and safe reload")


if __name__ == "__main__":
    check_sample()
    check_rejections()
