import json
import os
from flask import Flask, render_template, request

_path = os.path.dirname(__file__)

app = Flask(
    __name__,
    static_url_path="",
    static_folder=os.path.join(_path, "./frontend/"),
    template_folder=os.path.join(_path, "./frontend/"),
)
filename = "negative_examples.json"
#filename = "positive_examples.json"
items = json.load(open(f"data/{filename}"))
current_item_index = json.load(open("data/current_item_index.json"))


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/current_item/')
def current_item():
    return f"""
<textarea id="editor" name="editor" rows="40"
         class="block w-full px-0 text-sm text-gray-800 bg-white border-0 dark:bg-gray-800 focus:ring-0 dark:text-white dark:placeholder-gray-400"
         placeholder="Modify the item here"/>
{items[current_item_index]}
</textarea>
    """


@app.route('/next_item/')
def next_item():
    global current_item_index
    current_item_index += 1
    json.dump(current_item_index, open("data/current_item_index.json", "w"))
    return f"""
<textarea id="editor" name="editor" rows="40"
            class="block w-full px-0 text-sm text-gray-800 bg-white border-0 dark:bg-gray-800 focus:ring-0 dark:text-white dark:placeholder-gray-400"
            placeholder="Modify the item here"/>
{items[current_item_index]}
</textarea>
    """


@app.route('/previous_item/')
def previous_item():
    global current_item_index
    current_item_index -= 1
    json.dump(current_item_index, open("data/current_item_index.json", "w"))
    return f"""
<textarea id="editor" name="editor" rows="40"
            class="block w-full px-0 text-sm text-gray-800 bg-white border-0 dark:bg-gray-800 focus:ring-0 dark:text-white dark:placeholder-gray-400"
            placeholder="Modify the item here"/>
{items[current_item_index]}
</textarea>
    """


@app.route('/save_item/', methods=['GET'])
def save_item():
    global current_item_index
    items[current_item_index] = request.values['editor']
    json.dump(items, open(f"data/{filename}", "w"), indent=2)
    return ""


@app.route('/delete_item/')
def delete_item():
    global current_item_index
    items.pop(current_item_index)
    json.dump(items, open(f"data/{filename}", "w"), indent=2)
    return f"""
<textarea id="editor" name="editor" rows="40"
            class="block w-full px-0 text-sm text-gray-800 bg-white border-0 dark:bg-gray-800 focus:ring-0 dark:text-white dark:placeholder-gray-400"
            placeholder="Modify the item here"/>
{items[current_item_index]}
</textarea>
    """


if __name__ == '__main__':
    app.run(debug=True)
