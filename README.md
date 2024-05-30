# plugged-in
A simple utility primarily for gaming laptops which improves battery life on **windows 11 only**. Primarily for gaming laptops as it changes some power settings that drastically improves your battery life. I went from 2 hours SOT of browsing off of a full charge, to 9 hours with plugged-in running. 

PREREQUISITES:

- Have a fairly recent python + pip installed (thats it)
- ~~You MUST have nircmd installed for this to work, it's used for changing the brightness and refresh rate. It doesn't matter where, the program will find it, but make sure it is installed.~~ this is included in the powerplan installer ^
- ~~run the command 'pip install psutil screen_brightness_control pystray pillow winreg pywin32' for all required libraries.~~
  now automated as well ^

WHAT DOES IT DO:

- checks whether your laptop is plugged in to the wall or on battery power every 10 seconds
- changes powerplan to eco (disables dGPU entirely, limits CPU to 40% power, makes display turn off after 3 minutes idle and more) whilst on battery power.
- changes powerplan to high performance (optimises for performance, prioritises the use of the dGPU and lets the CPU run wild) whilst plugged in.
- changes refresh rate to 60 and sets brightness to 30 when on battery power (the brightness change is broken, goes to 60 whilst on battery and 30 when plugged in and I can't find the error)
- changes refresh rate to highest detected and sets brightness to 60 when plugged in(same issue, goes to 30)
- changes power mode (this is unique to windows 11. it is NOT the same as powerplan) to efficient or to max performance depending on the laptops plugged in state
- enables battery saver when laptop is unplugged
- 'high performance' toggle in system tray allows you to have similar performance to when plugged in but will wreck battery life so use sparingly
- can start on boot if you place a shortcut for the exe here: "C:\Users\YOURUSER\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
- MASSIVELY improves battery, at least in my experience.


INSTRUCTIONS

- see prerequisites
- if when you run/download it, it is detected as a virus, whitelist it. If you're worried, look at the source code and compile it yourself. I can't fix the false positive.
- run the aggressively named python file
- restart your laptop
- should now be working!

NOTES:
- I use a hardcoded version of this myself which includes my refresh of 165hz. The dynamic refresh rate finder and power plan *should* work, but if it doesn't, inform me and I'll try fix it.
- You need to download my powerplans as well for this to make much of a difference, a separate exectuable will be included which only needs to be ran ONCE. this is included as i dont want to ask for admin permissions every boot with the main program which would be really annoying, so this circumvents that.
- for some reason windows detects it as a virus but the source code is attached and can be compiled into an executable yourself with the following commands: 

   pip install pyinstaller
  pyinstaller --onefile --windowed PATHOFPLUGGEDIN
