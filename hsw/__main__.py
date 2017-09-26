import sys

from hsw import gui
import logging

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--pytest":
        import pytest  # type: ignore
        sys.exit(pytest.main(sys.argv[2:]))
    else:
        logging.root.setLevel(logging.DEBUG)
        logger = logging.getLogger(__name__)
        std_handler = logging.StreamHandler(sys.stdout)
        logging.root.addHandler(std_handler)
        logger.debug("Debug on")
        gui.main()


if __name__ == '__main__':
    main()
