# Atlas-VA

Atlas-VA is a simple project for training and running an intent detection model.

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Dependencies designed for Windows.
May also need to run ```winget install Gyan.FFmpeg```
May also need to install Visual Studio Build Tools from https://visualstudio.microsoft.com/downloads/?q=build+tools
and use the installer to install ```Desktop development with C++```.

## Training

train the models and create its weights:
```
nlu/intent_detection/training/pipeline
user_auth/wake_word_detection/training/pipeline
```

## Run the App

```
python3 app.py
```
