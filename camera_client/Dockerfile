FROM python:3.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /camera_client
WORKDIR /camera_client
ADD . /camera_client/
RUN pip install -r requirements.txt
CMD ["python", "manage.py", "runserver", "8000"]
EXPOSE 8000