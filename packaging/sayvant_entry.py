"""Einstieg für Sayvant.exe: ohne Argument die App im Infobereich, mit --settings das Einstellungsfenster."""
import sys

if __name__ == "__main__":
    if "--settings" in sys.argv:
        from sayvant.settings_app import main

        main(sys.argv[1:])
    else:
        from sayvant.app import main

        main()
