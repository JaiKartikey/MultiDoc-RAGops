# structure of dockerfile:
# 1
# ___GETTING IMAGE___ of starting point

# 2
# creating the ___WORKINGG DIRECTORY___

# 3
# ___GETTING UV___ from official page and putting in the PYTHON IMAGE 

# 4-5
# copying the ___REQUIREMENTS___ made using uv in the container
# uv sync

# 6
# now copying the actual ___APP & DATA___

# 7
# posting the data on ___PORT 8000___

# 8
# now run cmd


FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY app ./app
COPY data ./data

EXPOSE 8000

CMD [ "uv", "run", "uvicorn", "app.api.main:app","--host","0.0.0.0", "--port", "8000" ]


