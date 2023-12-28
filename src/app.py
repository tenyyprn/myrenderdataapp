from flask import Flask, request, render_template, redirect, url_for
import os
import pandas as pd

app = Flask(__name__, template_folder='templates')
server = app.server

UPLOAD_FOLDER = 'uploads'  # アップロードされたファイルを保存するディレクトリ

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# アップロード用のディレクトリが存在しない場合は作成する
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))  # ファイルを保存
            return redirect(url_for('dashboard', filename=file.filename))  # アップロード成功後にダッシュボードにリダイレクト
    return render_template('upload.html')

@app.route('/dashboard/<filename>')
def dashboard(filename):
    file_list = os.listdir(app.config['UPLOAD_FOLDER'])  # アップロードされたファイルの一覧を取得
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    data = pd.read_excel(file_path)  # アップロードされたExcelファイルを読み込む
    return render_template('dashboard.html', file_list=file_list, data=data.to_html())

@app.route('/')
def home():
    return render_template('upload.html')  # 最初にアップロードページを表示

if __name__ == '__main__':
    
    app.run(debug=True)