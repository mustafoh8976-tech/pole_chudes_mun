from connection_db import connection


async def add_user(tg_id, username):
	conn = await connection()
	if conn is None:
		return False

	try:
		await conn.execute('''
		insert into users(tg_id,username) values($1,$2)
		on conflict(tg_id) do update set username=excluded.username
		''', tg_id, username)
		return True
	except Exception as err:
		print('у вас не добавлен пользователь ошибка в:', err)
		return False
	finally:
		await conn.close()


async def get_words(count):
	conn = await connection()
	if conn is None:
		return None

	try:
		words = await conn.fetch('''
		select id,word,question from words order by random() limit $1
		''', count)
		return words
	except Exception as err:
		print('у вас не получены слова ошибка в:', err)
		return None
	finally:
		await conn.close()


async def add_game(tg_id, username, results):
	conn = await connection()
	if conn is None:
		return False

	try:
		user_id = await conn.fetchval('''
		insert into users(tg_id,username) values($1,$2)
		on conflict(tg_id) do update set username=excluded.username
		returning id
		''', tg_id, username)

		total = 0
		solved = 0
		for result in results:
			await conn.execute('''
			insert into games(user_id,word_id,score,is_win) values($1,$2,$3,$4)
			''', user_id, result['word_id'], result['score'], result['is_win'])
			total += result['score']
			if result['is_win']:
				solved += 1

		await conn.execute('''
		update users set score=score+$1,games=games+1,wins=wins+$2 where id=$3
		''', total, solved, user_id)
		print('игра сохранена')
		return True
	except Exception as err:
		print('у вас не сохранена игра ошибка в:', err)
		return False
	finally:
		await conn.close()


async def show_top():
	conn = await connection()
	if conn is None:
		return None

	try:
		users = await conn.fetch('''
		select username,score,wins from users
		where games>0 order by score desc limit 10
		''')
		return users
	except Exception as err:
		print('у вас не показан топ ошибка в:', err)
		return None
	finally:
		await conn.close()


async def get_stats(tg_id):
	conn = await connection()
	if conn is None:
		return None

	try:
		stats = await conn.fetchrow('''
		select score,wins,games from users where tg_id=$1
		''', tg_id)
		return stats
	except Exception as err:
		print('у вас не показан счёт ошибка в:', err)
		return None
	finally:
		await conn.close()