# Project Title

> eSpark Talent Backend
---------------------------
## Introduction

> The eSpark Talent Backend serves as the backbone for the eSpark Talent application, facilitating seamless talent management. This Django-powered backend provides essential functionalities for user authentication, profile management, and many other client employee base functionalities. Leveraging the Django Rest Framework and JWT authentication, the backend ensures secure and efficient communication between the front end and the database. This project aims to streamline talent-related processes, enhancing the overall user experience within the eSpark Talent ecosystem.
---------------------------
### Dependencies

> The eSpark Talent Backend relies on several key technologies and libraries to ensure optimal performance and functionality. Here are the core dependencies:

- Python:
``` 
 visit (https://www.python.org/downloads/) and install latest version of python 3.11
 
 ```

- Django
- Django Rest Framework
- Django Rest Framework Simple JWT
- drf-yasg Swagger generator

To install these dependencies, use the package manager pip with the provided requirements.txt file:

```
pip install -r requirements.txt

```
-------------------

### Installation 

- Clone the repo or download zip file

```
git clone https://github.com/eSpark-Consultants/esparkTalent-Backend-Development.git
cd eSparkTalent
```

- Install dependencies:

```
pip install -r requirements.txt

```

- Apply database migrations:

```
python manage.py migrate

```

- Run the development server:

```
python manage.py runserver

```

> The backend should now be accessible at http://localhost:8000/.

### Configuration

> Ensure that you configure the necessary settings in the settings.py file, including database configurations, security settings, and any other environment-specific variables

### Usage

> The backend provides various API endpoints for user authentication, home page data retrieval, and managing talent-related processes. Refer to the API documentation or Swagger UI for detailed information on available endpoints and their usage.

### API Documentation

> The API documentation, including detailed information about each endpoint, can be found in the Swagger UI. Access the Swagger UI at http://localhost:8000/swagger/.
