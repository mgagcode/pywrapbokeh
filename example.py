
from bokeh.layouts import column, row, layout, Spacer

from flask import Flask, redirect
from flask import request

from pywrapbokeh import WrapBokeh

app = Flask(__name__)
widgets = None


def _redirect_example_multi_select(value):
    if 'a' in value:   return "/a/"
    elif 'b' in value: return "/b/"
    elif 'c' in value: return "/c/"
    elif 'd' in value: return "/"
    else: return None


@app.route("/", methods=['GET'])
def test():
    d = widgets.dominate_document()

    args = request.args.to_dict()
    print(args)

    widgets.process_url(args)

    # redirect to another page based on widget data...
    _redirect = _redirect_example_multi_select(widgets.get_value("ms1"))
    if _redirect: return redirect(_redirect)

    doc_layout = layout(sizing_mode='scale_width')
    doc_layout.children.append(row(widgets.get_dom("Start"), Spacer(width=50), widgets.get_dom("End")))
    doc_layout.children.append(row(widgets.get_dom("Slider1"), widgets.get_dom("ms1")))

    d = widgets.render(d, doc_layout)
    return "{}".format(d)


@app.route("/c/", methods=['GET'])
@app.route("/b/", methods=['GET'])
@app.route("/a/", methods=['GET'])
def test_example():
    d = widgets.dominate_document()

    args = request.args.to_dict()
    print(args)

    widgets.process_url(args)

    # redirect to another page based on widget data...
    _redirect = _redirect_example_multi_select(widgets.get_value("ms1"))
    if _redirect: return redirect(_redirect)

    doc_layout = layout(sizing_mode='scale_width')
    doc_layout.children.append(row(widgets.get_dom("ms1")))

    d = widgets.render(d, doc_layout)
    return "{}".format(d)


widgets = WrapBokeh()

start = {"name": "Start", "title": "Start", "value": datetime.today(), "width": 150}
end   = {"name": "End",   "title": "End",   "value": datetime.today(), "width": 150}
widgets.add_datepicker_pair(start, end)

widgets.add_slider(name="Slider1", title="Age", value=25, start=1, end=99)

widgets.add_multi_select(name="ms1",
                         options=[('a', '1'), ('b', '2'), ('c', '3'), ('d', 'Home')],
                         size=2,
                         width=30)


app.run(host="0.0.0.0", port=6800)