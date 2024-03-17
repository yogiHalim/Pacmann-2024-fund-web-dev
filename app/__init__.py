from flask import Flask, render_template

vApp= Flask(__name__)
@vApp.route("/")
console.log(vApp.root_path)

def hello():   
    return render_template("contoh.html")
    return "Hello, world. Aaaagain"

# if __name__ == __main__:
#     vApp.run(host='0.0.0.0')