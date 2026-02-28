ROGUE_BUILD_DIR := rogue-collection/build/release

.PHONY: install build run clean

install:
	sudo apt-get update
	sudo apt-get install -y \
		build-essential \
		qtbase5-dev \
		qtdeclarative5-dev \
		qtmultimedia5-dev \
		qt5-qmake \
		qml-module-qtquick2 \
		qml-module-qtquick-controls \
		qml-module-qtquick-controls2 \
		qml-module-qtquick-layouts \
		qml-module-qtquick-dialogs \
		qml-module-qtquick-window2 \
		qml-module-qtmultimedia

build:
	$(MAKE) -C rogue-collection/src

run:
	cd $(ROGUE_BUILD_DIR) && LD_LIBRARY_PATH=. ./rogue-collection "Unix Rogue 5.4.2"

clean:
	$(MAKE) -C rogue-collection/src clean
