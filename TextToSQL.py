from groq import Groq
from sqlalchemy import create_engine
import pandas as pd, re

#https://www.mysqltutorial.org/wp-content/uploads/2023/10/mysqlsampledatabase.zip
engine = create_engine(f"mysql+pymysql://root:samp@localhost/classicmodels") 
client = Groq(api_key="gsk...")

def get_schema():
    return pd.read_sql(
        "SELECT TABLE_NAME AS `Table`, COLUMN_NAME AS `Column`, DATA_TYPE AS `Type` "+
        "FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'classicmodels' ORDER BY TABLE_NAME, ORDINAL_POSITION;",
        engine,
    )


def query_db(query):
    return pd.read_sql(
        re.search(r"```sql\n(.*?)\n```", query, re.DOTALL).group(1), engine
    )


def llm(question):
    return client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {
                "role": "user",
                "content": f"you are a sql engine\nwrite sql to answer the users question\nrespond in markdown format like "+
                f"```sql\nSELECT * FROM table\n```\nno yapping\n\nthe schema is: {get_schema()}\n\nQuestion: {question}",
            }
        ],
    ).choices[0].message.content


if __name__ == "__main__":
    resp = llm("How many customers with order count more than 5")
    print(query_db(resp))
