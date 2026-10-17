# CS 499 Milestone Four - Database Enhancement

## Artifact
This enhancement builds on the CS 340 Grazioso Salvare animal-shelter dashboard and its MongoDB data layer. The `original` folder contains the original CS 340 submission. The `enhanced` folder contains the Milestone Four database-focused version.

## Database Enhancements
- Added MongoDB indexes for animal ID, common rescue filters, and geolocation fields.
- Added server-side projection, pagination, and sorting support to reads.
- Added `count_documents()` support so record totals do not require downloading all matching documents.
- Added a MongoDB aggregation pipeline for top-breed reporting.
- Added a `$facet` aggregation for compact database summaries.
- Retained validation that blocks accidental empty-query update/delete operations by default.
- Retained environment-based credentials so passwords are not hard-coded in source files.
- Added automated tests for indexes, counts, aggregation, pagination, projection, sorting, and validation.
- Updated the dashboard so the breed chart is generated from MongoDB aggregation results rather than client-side `pandas.value_counts()`.

## Setup
1. Install packages: `pip install -r requirements.txt`
2. Set the environment variables shown in `.env.example`.
3. Run tests: `python -m unittest discover -s tests -v`
4. Open `ProjectTwoDashboard_Database_Enhanced.ipynb` and run the notebook in the course environment.

## Verification
The Python modules and test suite can be verified without the live course database. A final dashboard connection test must be performed in the Codio environment that contains the AAC MongoDB dataset and Dash/Jupyter dependencies.
