# Virtual ESP32 + Virtual P10

This version uses the authentication pattern shown by the current Django
API code: DRF Token authentication.

The current notice API returns:

{
    "success": true,
    "notice": {...}
}

## 1. Keep Django running

Example:

python manage.py runserver

## 2. Get an API token

Your APILoginView returns a token after a successful login.

Send a POST request to your existing login endpoint with the same email and
password used by the web application. Copy the returned `token`.

Example response:

{
    "success": true,
    "token": "PASTE_THIS_VALUE",
    "user": {...}
}

## 3. Put the token in config.py

API_TOKEN = "PASTE_THIS_VALUE"

Do not commit this token to GitHub.

## 4. Run

python -m pip install -r requirements.txt

python virtual_esp32.py

## Expected flow

Django -> CurrentNoticeAPIView -> Virtual ESP32 -> Virtual P10 x2

The simulator checks every 5 seconds and updates the virtual display only
when the notice changes.

## Important

This is a software/API simulation. It does not reproduce actual ESP32
GPIO timing, HUB75 electrical signals, scan mode, brightness or power usage.


## Virtual P10 animation

The two simulated P10 panels show the same notice simultaneously.
When a new notice arrives, the title is typed character-by-character,
then the message is typed character-by-character. The default speed is
about 90 ms per character.


## Two P10 panels as one display

The simulator treats the two physical P10 panels as a single continuous
128x16 virtual matrix:

[ P10 #1 64x16 ][ P10 #2 64x16 ]

The notice is NOT duplicated. Text is centered across the full combined
display, so the left portion appears on the first physical panel and the
right portion appears on the second physical panel.

The middle line is only a visual seam showing where the two physical
panels are joined.
