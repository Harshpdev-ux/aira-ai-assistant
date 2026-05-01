import serial
import speech_recognition as sr

# Configure the serial port (adjust COM port as needed, e.g., "COM3" for Windows or "/dev/ttyUSB0" for Linux)
arduino = serial.Serial(port="COM3", baudrate=9600, timeout=1)

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say 'on' or 'off' to control the LED:")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"You said: {command}")

        if "on" in command:
            arduino.write(b"on\n")  # Send "on" command
        elif "off" in command:
            arduino.write(b"off\n")  # Send "off" command
        else:
            print("Command not recognized.")
    
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError:
        print("Speech recognition service is unavailable")

# Run voice recognition in a loop
while True:
    recognize_speech()
