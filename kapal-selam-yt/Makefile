.PHONY: info tts preview render video thumb clean

info:
python build.py info

tts:
python build.py tts

# cek cepat satu bab: make preview ONLY=ch04
preview: tts
python build.py render --preview --only $(or $(ONLY),ch00)

render: tts
python build.py render

video:
python build.py all

thumb:
python build.py thumb

clean:
rm -rf build out media
