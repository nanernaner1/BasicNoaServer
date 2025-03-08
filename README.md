# BasicNoaServer
 For the Brilliant Labs Frame Glasses - a basic python handler for requests from the app.

This is a sample server that communicates with the Brilliant Labs Noa app that can be retrieved from the iOS App Store or the Google Play Store. The goal is to build an application that can use the Frames glasses as a 'mic' and 'camera' to communicate with a LLM running locally through Ollama or HuggingFace via HuggingFace Hub API over the public internet.

This is a work in progress and a personal project.

Currently tested successfully on an Android smartphone with Ollama providing inferencing with DeepSeek-r1:1.5b on a PC. While it is possible to run Ollama locally on the Android smartphone, the resource intensity seems to be too much for simultaneous audio transcription, text-to-speech, and Ollama inferencing. An attempt to wrap some of the processing in a Rust wrapper is in the works to see if this helps run entirely on a single device.
