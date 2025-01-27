@app.route('/course/<int:course_id>')
def course(course_id):
    sid = request.args.get('sid')
    if (type(sid) == NoneType):
        sid = -1
    else:
        if (auth.checkSID(int(sid))):
            sid = int(sid)
        else:
            sid = -1
    sid = request.args.get('sid')
    if (type(sid) == NoneType):
        sid = -1
    else:
        if (auth.checkSID(int(sid))):
            sid = int(sid)
        else:
            sid = -1
    course_file = os.path.join(COURSES_DIR, f"{course_id}.json")

    if not os.path.exists(course_file):
        abort(404, description="Course not found")

    with open(course_file, 'r', encoding='utf-8') as file:
        course_data = json.load(file)
        try:
            with open("relocate" + ".json", "r", encoding='utf-8') as f:
                relo = json.load(f)
        except FileNotFoundError:
            print("Файл не найден.")
        except json.JSONDecodeError:
            print("Ошибка декодирования JSON.")
    print(relo.get("Указательные местоимения", '#'))
    print(course_data)
    return render_template("course.html", course=course_data, course_id=course_id, relo=relo)
@app.route('/teory/<nomer>')
def teory(nomer):
    try:
        with open("teory/"+str(nomer)+".json", "r", encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Файл не найден.")
    except json.JSONDecodeError:
        print("Ошибка декодирования JSON.")
    try:
        with open("relocate"+".json", "r", encoding='utf-8') as f:
            relo = json.load(f)
    except FileNotFoundError:
        print("Файл не найден.")
    except json.JSONDecodeError:
        print("Ошибка декодирования JSON.")
    print(data)
    return render_template('teory.html', teory = data, relo = relo)
