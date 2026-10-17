CS 499 Milestone Four - Christopher Wright
Enhancement Three: Databases

SUBMISSION CONTENTS
1. original/ - original CS 340 artifact before capstone enhancements
2. enhanced/ - Milestone Four database-focused artifact
3. Separate Word document: CS499_Milestone_Four_Database_Narrative_Christopher_Wright.docx

KEY DATABASE ENHANCEMENTS
- MongoDB indexes for animal ID, rescue filtering, and location
- Server-side projection, pagination, and sorting
- count_documents for efficient totals
- Aggregation pipeline for breed reporting
- Faceted database summary aggregation
- Input validation and protection against accidental mass updates/deletes
- Environment-based database credentials
- Automated database/service tests
- Dashboard chart uses MongoDB aggregation rather than client-side counting

TESTING
Run from the enhanced folder:
    python -m unittest discover -s tests -v

The live dashboard/database connection should also be run in Codio because the AAC MongoDB database and course environment are hosted there.
