# Use an official Python runtime as a parent image
FROM python:3.11
ENV SECRET_KEY='secret'
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["bash", "-c", "flask db upgrade && python3 -m flask run --host=0.0.0.0"]
