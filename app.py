from flask import Flask, request, render_template, flash, redirect, url_for
from flask_bootstrap import Bootstrap

from config import BaseConfig
from forms import StartForm, FinishForm, GameForm
from text_game import TextQuest

app = Flask(__name__)
global gamer

app.config.from_object(BaseConfig)
bootstrap = Bootstrap(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    '''
    Функция главной страницы.
    Отображает приветствие, и просит игрока ввести своё имя,
    которое будет использоваться в завершении игры.
    '''
    global gamer
    form = StartForm()
    if request.method == "POST" and form.validate_on_submit():
        # Тут надо заново создать нашего одиночку, чтобы игра начиналась всегда с начала.
        TextQuest(True)
        gamer = form.gamer_name.data
        return redirect(url_for("game", finish=0))
    return render_template('index.html', form=form)


@app.route('/game/<int:finish>', methods=['GET', 'POST'])
def game(finish=0):
    '''
    Основная функция игры, пока игра не закончена выдает шаблон game.html, по завершению выдает endgame.html
    с которого можно будет вернуться на главную страницу.
    '''
    global gamer
    # Костылик, защищающий сервер от обращения сразу сюда, без захода с главной страницы
    # Поскольку глобальная переменная gamer инициализируется в index, то если Index не вызывался
    # переменная не определена, вот и попробуем к ней обратиться, если NameError, то редирект на index
    # конечно правильнее было бы на index ставить куку сессии и тут её проверять, но это учебный проект,
    # незачем его черезчур усложнять.
    try:
        gamer == 1
    except NameError:
        return redirect(url_for('index'))
    # конец костыля
    game_class = TextQuest()
    game_form = GameForm()

    # Проверяем не закончена ли игра
    if finish:
        finish_form = FinishForm()
        if request.method == "POST" and finish_form.validate_on_submit():
            return redirect(url_for('index'))
        return render_template("endgame.html",
                               gamer=gamer,
                               moves=game_class.moves,
                               endgame_text=game_class.end_text(),
                               form=finish_form)

    # Если игра только началась, выводим привественные сообщения
    # Стартовые -1 требуются чтобы приветственные сообщения не висели постоянно,
    # до первого удачного хода.
    if game_class.moves == -1:
        flash("Добро пожаловать в игру", "primary")
        flash(game_class.start_text(), "success")
        game_class.moves = 0

    # Теперь если мы получили POST с движениями, то надо их обработать.
    if request.method == "POST" and game_form.validate_on_submit():
        for move in range(game_form.moves.data):
            # Двигаем персонажа и выдаем сообщение
            move_data = game_class.move(game_form.direction.data)
            if move_data == 1:
                flash(f"{game_class.get_room_decs()}{game_class.check_visited()}", "success")
            elif move_data == 2:
                flash(game_class.wrong_move_text(), 'danger')
                break
            elif move_data == 3:
                return redirect(url_for("game", finish=1))
    return render_template('game.html', form=game_form)


if __name__ == '__main__':
    app.run()
