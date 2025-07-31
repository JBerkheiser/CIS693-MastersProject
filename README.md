# CIS693 Masters Project
This project was developed as a showcase of what I had learned throughout my education as a computer scientist.  The project is a proof-of-concept of a cloud-based virtual assistent that can answer questions and process images.

## How It's Made

**Frontend:** The frontend was developed using a Raspberry Pi Zero 2w, as it was a compact and lightweight computer, and the project would not require much processing power.  The IQaudIO Pi-Codec Zero was selected to process input and output audio.  Voice input is accepted via the onboard microphone, and audio is output via the mono-speaker driver.  In order to process images, the Raspberry Pi Camera Module 3 was used.  

The fronted software was written in Python, and was developed to be readable and modular.  The main function included a finite state machine to separate the different steps of the frontends process.  When powered on, the project continually records and processes audio until a wakeword is detected.  For this project, a one wakeword, "Hey Torkleson", was selected for when the user wants to ask a question.  Another, "Jarvis", was selected for when the user wants a photo to be taken and processed.  The code then send the correct information to the backend and wait for the response.  The response is a link to the backends downloadable audio.  The frontend downloads the audio and plays the response to the user.  This process is then repeated.

**Backend:** The backend of the project was developed predominantly on Google Cloud Platform.  The App Engine was used to create the endpoint that interacted with the frontend.  If the user asks the project a question, the audio bytes are processed into a text query using Google Clouds speech client.  This text query is then given to Google's Gemini 2.0 model where a response is generated.  The response is converted from text to audio via Resemble's text-to-speech software.  The link to download that audio is then returned to the frontend.

## Lessons Learned


## Optimizations to be made
- Refactor backend
- Can it be done faster? (No cold starts, could save ~15 secs)
