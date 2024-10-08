# 
FROM python:3.10

# 
WORKDIR /app

# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN pip install -r /code/requirements.txt

# 
COPY . .

CMD ["ls"]

EXPOSE 443
