#Python script at the top-level that defines the Flask application instance --> imports the application instance
from app import app
from app.models import Test
from flask import Flask, render_template, url_for, request, redirect

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        test_content = request.form['content']
        new_test = Test(content = test_content)

        try:
            db.session.add(new_test)
            db.session.commit()
            return redirect('/')
        except:
            'There was an error adding the test data to the database.'
    else:
        tests = Test.query.all()
        return render_template('index.html', tests=tests)

if __name__ == "__main__":
    app.run(host='0.0.0.0')