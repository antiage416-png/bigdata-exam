import sys
import os

base = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base)

print("1. Checking file existence...")
expected_files = [
    'app.py', 'requirements.txt', 'README.md', 'data/questions.json',
    'utils/data_generator.py', 'utils/code_runner.py', 'utils/grader.py', 'utils/storage.py',
    'modules/exam_1.py', 'modules/exam_2.py', 'modules/exam_3.py', 'modules/exam_mock.py',
    'modules/cheat_sheet.py', 'modules/dashboard.py'
]

for rel_path in expected_files:
    full_path = os.path.join(base, rel_path)
    assert os.path.exists(full_path), f"Missing: {full_path}"
    print(f"  [OK] {rel_path}")

print("2. Testing module imports...")
import utils.data_generator
import utils.code_runner
import utils.grader
import utils.storage
import modules.exam_1
import modules.exam_2
import modules.exam_3
import modules.exam_mock
import modules.cheat_sheet
import modules.dashboard
print("  [OK] All modules imported cleanly without syntax or import errors!")

print("3. Testing Question Bank loading...")
bank = utils.storage.load_question_bank()
print(f"  [OK] Loaded {len(bank['type1'])} Type 1 questions, {len(bank['type2'])} Type 2 questions, {len(bank['type3'])} Type 3 questions, {len(bank['mock_exams'])} mock exams")

print("4. Testing History Save and Load...")
rec = utils.storage.save_exam_result(
    exam_name="Self-Test Mock Exam",
    total_score=85.0,
    max_score=100.0,
    type1_score=30.0,
    type2_score=40.0,
    type3_score=15.0,
    time_spent_seconds=3600,
    details={"test": True}
)
hist = utils.storage.load_exam_history()
assert len(hist) >= 1, "History saving failed"
print(f"  [OK] History test record saved and loaded successfully: {hist[-1]['exam_name']}")

print("\n>>> ALL BACKEND SELF-TESTS PASSED SUCCESSFULLY! <<<")
