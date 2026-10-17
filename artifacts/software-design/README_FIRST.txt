CS 499 Milestone Two - Christopher Wright
Software Design and Engineering Enhancement

WHAT IS INCLUDED

original/
- CRUD_Python_Module.py
- ProjectTwoDashboard.ipynb

enhanced/
- CRUD_Python_Module.py
- config.py
- repository.py
- service.py
- exceptions.py
- ProjectTwoDashboard_Enhanced.ipynb
- tests/test_service.py
- .env.example
- requirements.txt

Separate Word narrative:
- CS499_Milestone_Two_Narrative_Christopher_Wright.docx

ENHANCEMENT SUMMARY
The original single CRUD class was refactored into a layered design with separate
configuration, repository/data-access, business logic/validation, custom exceptions,
logging, type hints, secure environment-based credentials, and automated unit tests.
The updated dashboard keeps the familiar AnimalShelter CRUD interface while using
the enhanced architecture.

LOCAL/CODIO SETUP
1. Put the enhanced files in the same project directory.
2. Install packages if needed:
   pip install -r requirements.txt
3. Set MongoDB environment variables before launching the dashboard:
   export AAC_USERNAME=aacuser
   export AAC_PASSWORD='YOUR_PASSWORD'
   export AAC_HOST=localhost
   export AAC_PORT=27017
   export AAC_DATABASE=aac
   export AAC_COLLECTION=animals
   export AAC_AUTH_SOURCE=admin
4. Run the unit tests:
   python -m unittest discover -s tests -v
5. Open ProjectTwoDashboard_Enhanced.ipynb and run the cells.

TESTING COMPLETED HERE
- 7 service-layer unit tests passed.
- All enhanced Python files passed Python syntax compilation checks.

IMPORTANT
The live MongoDB/Dash connection still needs to be tested in your Codio environment,
because that environment contains the MongoDB server, course database, and dashboard
packages used by the original project.
