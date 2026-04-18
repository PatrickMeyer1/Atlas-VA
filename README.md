# Atlas-VA

Atlas-VA is a simple project for training and running an intent detection model.

## Setup

Install dependencies:

Dependencies designed for Windows.
Run ```winget install Gyan.FFmpeg```
Install Visual Studio Build Tools from https://visualstudio.microsoft.com/downloads/?q=build+tools
and use the installer to install ```Desktop development with C++```.

```bash
python -m pip install --upgrade pip setuptools wheel
pip install torch==2.11.0+cu128 torchaudio==2.11.0+cu128 --extra-index-url https://download.pytorch.org/whl/cu128
pip install -r requirements.txt
pip install nemo-toolkit==2.7.2 --no-deps # Only if you want to try testing with nemo
```

You will also need to add two tokens to the .env, in the format as described in the ```.env.example``` file. One, is a
huggingface token. Be sure to request access for the ```meta-llama/Llama-3.2-1B``` model. The second is a Perenual
API key, which you get from: https://perenual.com/docs/api.

## Training

train the models and create its weights:
```
nlu/intent_detection/training/pipeline
user_auth/wake_word_detection/training/pipeline
```

Run using ```python pipeline.py```.

## Run the App

```
python3 app.py
```
