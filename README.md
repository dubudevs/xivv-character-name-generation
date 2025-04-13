# xivv-character-name-generation
Regenerate XIVVoices lines using the built in voicelines as reference audio using F5-TTS, but with your own character's name inserted where applicable. 

This code sucks a lot lol

You will need F5-TTS to use this: https://github.com/SWivid/F5-TTS/

Get the data:
Run step 1, point it at the XIVV/Data folder, it will then grab all of the files that contain Arc or \_NAME\_ and backup the oggs for restoration later if wanted, and convert the oggs to wavs and place the jsons with them. This is for faster inference later. This should return ~11k files right now

Run step 1.5, this will replace problematic words with ones which are pronounced better. This is very WIP, but I believe almost all of these are an upgrade. 

Inference:
Run step 2 after replacing the specified name at the top with a PHONETIC version of your character's name. Using ' can work quite well for forcing syllable breaks without adding a pause, and note that upper case letters are pronounced differently, so miqo'te names should generally use a lowercase first letter and an ' to force it to say the first letter separately. Try it out and see, the script will only generate lines which contain your character name so try different variations and let it generate some and see what works. It probably won't be the first one you try. eg my character name is V'zixa but v'zicksa was the best option for me in my testing. If you have a normal human name then you are in luck, unless its pronounced differently. Alisaie generally pronounces better for me, but Alphinaud often works less well, so you might want to wait for it to generate some Alphinaud lines to check how it performs once you get a version that works with Alisaie. Not sure why Alphinaud is so bad, its the worst of everyone I believe, for now.

Modify `nfe_step` to adjust the speed of inference. This adjusts VRAM usage, 64 is the slowest but is slightly less noisy, 32 is a nice middle ground imo, 16 is slightly noisier but is faster still, you can also go lower if you're on low end hardware. 32 gives me 1.2-1.4s generations on my 3080.

Finally:
Run step 3 - sorry, I had to run this through chatgpt a few times to fix a bug that wasn't with the code but the sf library. This is very slow compared to using sf but it would break often for no good reason, so ffmpeg it is. 

Once you have FinalOggData just open it and ctrl+A and go into XIVV/Data and ctrl+V and click overwrite files. Or if you aren't on windows or you prefer to you can write a script to copy them.

Any questions message me on discord I'm in the XIVV server.
