FROM python:3.11.7-alpine3.18
WORKDIR /app
COPY ./ /app
RUN pip3 install -r requirements.txt
EXPOSE 5000
CMD ["python3", "app.py"]