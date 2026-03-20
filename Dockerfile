FROM python:3.12-alpine

# Устанавливаем системные зависимости для psycopg2
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev 

WORKDIR /code

# Указываем зеркало PyPI (наблюдается проблема с загрузкой пакетов)
ENV PIP_INDEX_URL=https://pypi.mirrors.ustc.edu.cn/simple
ENV PIP_TRUSTED_HOST=pypi.mirrors.ustc.edu.cn
ENV UV_INDEX_URL=https://pypi.mirrors.ustc.edu.cn/simple

COPY pyproject.toml uv.lock ./

RUN pip install uv && uv sync --frozen

COPY . .

ENV PATH="/code/.venv/bin:$PATH"

CMD ["alembic", "-c", "app/alembic.ini", "upgrade", "head"]