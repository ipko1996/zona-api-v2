# 🍽️ [Zona API](https://zona-api.up.railway.app/)

The "API" was created for the Zóna restaurant in Veszprém, which processes and serves the weekly uploaded pictures on [Facebook](https://www.facebook.com/zonaetterem) in a table or JSON format.

### 🐍 Prerequirements

- [python3](https://www.python.org/downloads/)
- [git](https://git-scm.com/downloads)

### Good to know

- [selinium](https://www.selenium.dev/) (used for scraping)
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) (creating text from image)
- [FastAPI](https://fastapi.tiangolo.com/) (python api framework)
- _42 is always a good answer_

## Install

```
git clone https://github.com/ipko1996/zona-api.git
cd zona-api
```

**create a virtual python environment**

```
pip install -r requirements.txt
```

**Install separately**

```
pip install git+https://github.com/JaidedAI/EasyOCR.git
```

**🦄 Run**

```
uvicorn main:app --reload
```

Go to

- /docs - swagger 📜
- / - an apple 🍎
- /weekly_meal - the menu in json format
- /weekly_meal/table - a nice table like format for the humans 🙆
  
