FROM python:3

COPY  . /app
WORKDIR /app
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "censys_subdomain_finder.py"]
CMD ["-h"]