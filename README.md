# Christopher Wright Computer Science ePortfolio

The readable portfolio begins at `index.html`. It presents the professional self-assessment first, then two artifacts enhanced across three categories, source comparisons, course outcome evidence, and verification limits.

## Publish

Upload these files to the root of [https://github.com/ChristopherWright1211/CS-499-Computer-Science-Capstone](https://github.com/ChristopherWright1211/CS-499-Computer-Science-Capstone), preserving unrelated work. In Settings → Pages choose Deploy from a branch, main, /(root). Expected address: https://christopherwright1211.github.io/CS-499-Computer-Science-Capstone/ (not yet verified).

## Required before submission

- Add the actual code review video URL to `portfolio-config.json`.
- Apply any instructor feedback not supplied with this package.
- Verify MongoDB and the dashboard in Codio.
- Open the published URL and check all navigation and downloads.

## Artifacts

- Software design: `artifacts/software-design` contains original code and the layered enhancement.
- Algorithms: `artifacts/algorithms` contains original and enhanced C++ source, sample input, and integration checks.
- Databases: `artifacts/databases` contains original code and the final database enhancement.

## Run checks

Run `python3 -m unittest discover -s tests -v` in each Python enhanced folder. For algorithms, run `g++ -std=c++17 -Wall -Wextra -Wpedantic -O2 ProjectTwo_Enhanced.cpp -o course_planner`, then `python3 test_planner.py`.

Read [VERIFICATION.md](VERIFICATION.md) for scope and [the submission guide](documents/Publication_and_Submission_Guide.docx) for remaining steps. Original public dashboard copies mask credentials and clear outputs; their logic is otherwise retained. No live database or student dataset is bundled.

AI acknowledgment: ChatGPT assisted with final narrative revisions, website assembly, and verification. The earlier algorithms milestone also acknowledges AI-assisted code and documentation.
