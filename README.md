**pywrapbokeh**

A python class for wrapping bokeh widgets in a Flask app so that all callbacks can be in python rather than in HTML/javascript, because I just don't want to learn javascript.

LOOK Ma! No HTML! No Javascript! No JQuery!

**Installation**
```buildoutcfg
pip install -r < requirements.txt
```

**Hello World**
```buildoutcfg
python ex1_hello_world.py
```

**Many Widgets example**
```buildoutcfg
python ex_main.py
```

**bokeh** is an awesome package, and you should try out the many online examples and tutorials before using this framework.
https://bokeh.pydata.org/en/latest/

How It Works:
Every bokeh widget callback is assigned a bit of (common) javascript that causes a web refresh with all the widget parameters in the URL. In this way the Flask route can scrape the URl and get all widget parameters and handle them in python.

---

pywrapbokeh, Copyright (c) 2018, Martin Guthrie, All Rights Reserved
License: MIT License



