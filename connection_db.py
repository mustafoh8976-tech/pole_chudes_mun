from dotenv import load_dotenv
import asyncpg
import os


load_dotenv()


async def connection():
	try:
		conn = await asyncpg.connect(
			user=os.getenv('DB_USER'),
			password=os.getenv('DB_PASSWORD'),
			port=int(os.getenv('DB_PORT')),
			host=os.getenv('DB_HOST'),
			database=os.getenv('DB_NAME')
		)
		print('подключено в БД')
		return conn
	except Exception as err:
		print('у вас ошибка в БД:', err)
		return None


async def create_table():
	conn = await connection()
	if conn is None:
		return False

	try:
		await conn.execute('''
		create table if not exists users(
			id serial primary key,
			tg_id bigint unique not null,
			username varchar(100),
			score int default 0,
			wins int default 0,
			games int default 0
		);
		create table if not exists words(
			id serial primary key,
			word varchar(50) not null,
			question text not null
		);
		create table if not exists games(
			id serial primary key,
			user_id int references users(id) on delete cascade,
			word_id int references words(id),
			score int default 0,
			is_win bool default false,
			created_at timestamp default now()
		);
		''')

		words = [
			('ЖИРАФ', 'Самое высокое животное на планете'),
			('ПИНГВИН', 'Птица, которая не летает, но отлично плавает'),
			('ВЕРБЛЮД', 'Корабль пустыни'),
			('САМОВАР', 'Русский прибор для кипячения воды'),
			('МАТРЕШКА', 'Деревянная кукла, внутри которой другие куклы'),
			('БАЛАЛАЙКА', 'Русский народный трёхструнный инструмент'),
			('ГЛОБУС', 'Модель Земли в виде шара'),
			('ТЕЛЕСКОП', 'Прибор, чтобы смотреть на звёзды'),
			('ШОКОЛАД', 'Сладкое лакомство из какао-бобов'),
			('ВУЛКАН', 'Гора, из которой извергается лава'),
			('КРОКОДИЛ', 'Хищная рептилия, живёт в тёплых реках'),
			('ПАРАШЮТ', 'Спасает при прыжке с большой высоты'),
			('ЛАБИРИНТ', 'Запутанная система ходов, из которой трудно выбраться'),
			('КОМПЬЮТЕР', 'Электронная машина для вычислений и игр'),
			('МОРОЖЕНОЕ', 'Холодное лакомство в стаканчике или на палочке'),
			('ЛОКОМОТИВ', 'Тянет за собой вагоны поезда'),
			('ПОДСОЛНУХ', 'Жёлтый цветок, который поворачивается за солнцем'),
			('ОРАНГУТАН', 'Рыжая человекообразная обезьяна из Азии'),
			('ВЕЛОСИПЕД', 'Двухколёсный транспорт, на котором едут, крутя педали'),
			('КАЛЕЙДОСКОП', 'Трубка с цветными стёклышками, которые складываются в узоры'),
			('АКВАРИУМ', 'Стеклянный дом для рыбок'),
			('ПЛАНЕТА', 'Земля, Марс и Венера - это...'),
			('ХОЛОДИЛЬНИК', 'Кухонный шкаф, в котором продукты хранятся холодными'),
			('САЛЮТ', 'Праздничные огни в ночном небе'),
			('ПЫЛЕСОС', 'Бытовой прибор, который втягивает мусор с пола'),
			('МАЯК', 'Башня на берегу, которая указывает кораблям путь'),
			('БУМЕРАНГ', 'Изогнутая палка, которая возвращается к бросившему'),
			('ЗЕБРА', 'Лошадиное животное в чёрно-белую полоску'),
			('ОГУРЕЦ', 'Зелёный овощ, который солят на зиму'),
			('КЕНГУРУ', 'Австралийское животное с сумкой для детёныша'),
		]
		await conn.executemany('''
		insert into words(word,question)
		select $1::varchar,$2::text
		where not exists(select 1 from words where word=$1::varchar)
		''', words)
		print('слова добавлены')

		print('таблицы созданы')
		return True
	except Exception as error:
		print('у вас не созданы таблицы ошибка в:', error)
		return False
	finally:
		await conn.close()