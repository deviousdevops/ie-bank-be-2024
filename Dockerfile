# Use an official Python runtime as a parent image
FROM python:3.11
ENV SECRET_KEY='secret'
ENV PORT=8000
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=8000"]
