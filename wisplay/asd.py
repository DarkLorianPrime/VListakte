import asyncio

from databases import Database

from project.libraries.database import *


async def wait():
    database = await get_database_instance()
    #query = """CREATE TABLE %s (id SERIAL PRIMARY KEY , name VARCHAR(100), score INTEGER)"""
    #await database.execute(query=query % "hellos")
    # query = "INSERT INTO HighScores(name, score) VALUES (:name, :score)"
    # values = [
    #     {"name": "Daisy", "score": 92},
    #     {"name": "Neil", "score": 87},
    #     {"name": "Carol", "score": 43},
    # ]
    await create_one_entry(db=database, tablename="HighScores", values={"name": "Carol", "score": 43})
    # await database.execute_many(query=query, values=values)
    # rows = await get_all_entries(db=database, tablename="highscores")
    # print('High Scores:\n' + ",\n".join([f'{i["name"]} {i["score"]}' for i in rows]))


asyncio.get_event_loop().run_until_complete(wait())