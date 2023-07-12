# base image  
FROM python:3.9.6  
RUN mkdir /sps-master
WORKDIR /sps-master
ADD . /sps-master/
RUN pip install -r requirements.txt
CMD ["python", "manage.py", "runserver", "8000"]
EXPOSE 8000