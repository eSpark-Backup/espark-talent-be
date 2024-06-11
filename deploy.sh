cd /my_project;
source env/bin/activate; #activate your virtual envirement
cd eSparkTalent
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8000